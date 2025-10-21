#!/usr/bin/bash
#
# This test script runs integration tests for the LMCache integration with vLLM.
# A lmcache/vllm-openai container image is built by this script from the LMCache code base
# the script is running from and the latest nightly build of vLLM. It is therefore using the
# latest of both code bases to build the image which it then performs tests on.
#
# It’s laid out as follows:
# - UTILITIES:  utility functions
# - TESTS:      test functions
# - SETUP:      environment setup steps
# - MAIN:       test execution steps
#
# It requires the following to be installed to run:
# - curl
# - docker engine (daemon running)
# - NVIDIA Container Toolkit:
#   https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
#
# Note: The script should be run from the LMCache code base root.
# Note: L4 CI runners cannot use Flash Infer

set -e
trap 'cleanup $?' EXIT

CID=
HF_TOKEN=
SERVER_WAIT_TIMEOUT=180
PORT=

#############
# UTILITIES #
#############

cleanup() {
    local code="${1:-0}"

    echo "→ Cleaning up Docker containers and ports..."

    # Clean up container IDs if defined
    for cid_var in CID PREFILLER_CID DECODER_CID; do
        local cid="${!cid_var:-}"
        if [[ -n "$cid" ]]; then
            docker kill "$cid" &>/dev/null || true
            docker rm "$cid" &>/dev/null || true
        fi
    done

    # Clean up ports if defined
    for port_var in PORT PORT1 PORT2; do
        local port="${!port_var:-}"
        if [[ -n "$port" ]]; then
            fuser -k "${port}/tcp" &>/dev/null || true
        fi
    done
}

find_available_port() {
    local start_port=${1:-8000}
    local port=$start_port

    while [ $port -lt 65536 ]; do
        # Check if port is available using netstat
        if ! netstat -tuln 2>/dev/null | grep -q ":${port} "; then
            # Double-check by trying to bind to the port with nc
            if timeout 1 bash -c "</dev/tcp/127.0.0.1/${port}" 2>/dev/null; then
                # Port is in use, try next one
                ((port++))
                continue
            else
                # Port is available
                echo $port
                return 0
            fi
        fi
        ((port++))
    done

    echo "ERROR: No available ports found starting from $start_port" >&2
    return 1
}

build_lmcache_vllmopenai_image() {
    cp example_build.sh test-build.sh
    chmod 755 test-build.sh
    ./test-build.sh
}

wait_for_openai_api_server() {
    local port="$1"
    local model="$2"
    local cid="$3"

    if ! timeout "$SERVER_WAIT_TIMEOUT" bash -c "
        echo \"Curl /v1/models endpoint\"
        until curl -s 127.0.0.1:${port}/v1/models \
                | grep -Fq \"\\\"id\\\":\\\"${model}\\\"\"; do
            sleep 30
        done
        echo \"Model ${model} is available on ${port}\"
    "; then
        echo "OpenAI API server did not start"
        docker logs $cid
        return 1
    fi
}

run_lmcache_vllmopenai_container() {
    local docker="$1"
    local vllm="$2"
    local cfg_name="$3"
    LOGFILE="/tmp/build_${BUILD_ID}_${cfg_name}.log"

    # Pick the GPUs based on config
    gpu_count=$(yq -r '.docker.gpu_count // 1' "$cfg_file")
    source "$ORIG_DIR/.buildkite/scripts/pick-free-gpu.sh" "" "$gpu_count"
    best_gpu="${CUDA_VISIBLE_DEVICES}"

    # docker args
    docker_args=(
        --runtime nvidia
        --network host
        --gpus "\"device=${best_gpu}\""
        --volume ~/.cache/huggingface:/root/.cache/huggingface
        --volume "${CONFIG_DIR}/lmcache_configs:/etc/lmcache:ro"
        --env VLLM_USE_FLASHINFER_SAMPLER=0
        --env HF_TOKEN="$HF_TOKEN"
    )
    while IFS= read -r e; do
        [[ -n $e ]] && docker_args+=(--env "$e")
    done < <(yq -r '.env[]?' <<<"$docker")

    # vllm args
    vllm_model="$(yq -r '.model' <<<"$vllm")"
    mapfile -t vllm_cli_args < <(yq -r '.args // [] | .[]' <<<"$vllm")
    cmd_args=(
        lmcache/vllm-openai:build-latest
        "$vllm_model"
    )
    cmd_args+=("${vllm_cli_args[@]}")
    cmd_args+=("--port" "$PORT")

    # Start docker
    CID=$(
        docker run -d \
            "${docker_args[@]}" \
            "${cmd_args[@]}"
    )

    wait_for_openai_api_server "$PORT" "$vllm_model" "$CID"

    # Logging
    touch "$LOGFILE"
    docker logs -f "$CID" >>"$LOGFILE" 2>&1 &
    LOG_PID=$!
}

run_pd_lmcache() {
    local prefiller_docker="$1"
    local prefiller_vllm="$2"
    local decoder_docker="$3"
    local decoder_vllm="$4"
    local cfg_name="$5"
    PREFILLER_LOGFILE="/tmp/build_${BUILD_ID}_${cfg_name}_prefiller.log"
    DECODER_LOGFILE="/tmp/build_${BUILD_ID}_${cfg_name}_decoder.log"

    ########## Prefiller ##########
    # docker args
    prefiller_docker_args=(
        --runtime nvidia
        --network host
        --gpus "device=0"
        --volume ~/.cache/huggingface:/root/.cache/huggingface
        --env VLLM_USE_FLASHINFER_SAMPLER=0
        --env HF_TOKEN="$HF_TOKEN"
        --env UCX_TLS=cuda_ipc,cuda_copy,tcp
        --ipc host
        --shm-size 4G
    )
    while IFS= read -r e; do
        [[ -n $e ]] && prefiller_docker_args+=(--env "$e")
    done < <(yq -r '.env[]?' <<<"$prefiller_docker")
    proxy=$(yq -er '."proxy-port"' <<<"$prefiller_docker" 2>/dev/null)
    prefiller_docker_args+=(--env "LMCACHE_PD_PROXY_PORT=$proxy")

    # vllm args
    prefiller_vllm_model="$(yq -r '.model' <<<"$prefiller_vllm")"
    mapfile -t prefiller_vllm_cli_args < <(yq -r '.args // [] | .[]' <<<"$prefiller_vllm")
    prefiller_cmd_args=(
        lmcache/vllm-openai:build-latest
        "$prefiller_vllm_model"
    )
    prefiller_cmd_args+=("${prefiller_vllm_cli_args[@]}")
    prefiller_cmd_args+=("--port" "$PORT1")

    # Start docker
    PREFILLER_CID=$(
        docker run -d \
            "${prefiller_docker_args[@]}" \
            "${prefiller_cmd_args[@]}"
    )

    # Health check
    wait_for_openai_api_server "$PORT1" "$prefiller_vllm_model" "$PREFILLER_CID"

    # Logging
    touch "$PREFILLER_LOGFILE"
    docker logs -f "$PREFILLER_CID" >>"$PREFILLER_LOGFILE" 2>&1 &

    ########## Decoder ##########
    # docker args
    decoder_docker_args=(
        --runtime nvidia
        --network host
        --gpus "device=1"
        --volume ~/.cache/huggingface:/root/.cache/huggingface
        --env VLLM_USE_FLASHINFER_SAMPLER=0
        --env HF_TOKEN="$HF_TOKEN"
        --env UCX_TLS=cuda_ipc,cuda_copy,tcp
        --ipc host
        --shm-size 4G
    )
    while IFS= read -r e; do
        [[ -n $e ]] && decoder_docker_args+=(--env "$e")
    done < <(yq -r '.env[]?' <<<"$decoder_docker")
    init=$(yq -er '."init-port"' <<<"$decoder_docker" 2>/dev/null)
    decoder_docker_args+=(--env "LMCACHE_PD_PEER_INIT_PORT=$init")
    alloc=$(yq -er '."alloc-port"' <<<"$decoder_docker" 2>/dev/null)
    decoder_docker_args+=(--env "LMCACHE_PD_PEER_ALLOC_PORT=$alloc")

    # vllm args
    decoder_vllm_model="$(yq -r '.model' <<<"$decoder_vllm")"
    mapfile -t decoder_vllm_cli_args < <(yq -r '.args // [] | .[]' <<<"$decoder_vllm")
    decoder_cmd_args=(
        lmcache/vllm-openai:build-latest
        "$decoder_vllm_model"
    )
    decoder_cmd_args+=("${decoder_vllm_cli_args[@]}")
    decoder_cmd_args+=("--port" "$PORT2")

    # Start docker
    DECODER_CID=$(
        docker run -d \
            "${decoder_docker_args[@]}" \
            "${decoder_cmd_args[@]}"
    )

    # Health check
    wait_for_openai_api_server "$PORT2" "$decoder_vllm_model" "$DECODER_CID"

    # Logging
    touch "$DECODER_LOGFILE"
    docker logs -f "$DECODER_CID" >>"$DECODER_LOGFILE" 2>&1 &

    ########## Proxy ##########
    if [ ! -d ".venv" ]; then
        UV_PYTHON=python3 uv -q venv
    fi
    source .venv/bin/activate
    uv pip install -r "$ORIG_DIR/requirements/build.txt" > /dev/null 2>&1
    uv pip install torch==2.7.1 httpx fastapi uvicorn > /dev/null 2>&1
    uv pip install -e "$ORIG_DIR" --no-build-isolation > /dev/null 2>&1
    # Start proxy
    python3 "$ORIG_DIR/examples/disagg_prefill/disagg_proxy_server.py" \
        --port "$PORT" \
        --prefiller-port "$PORT1" \
        --decoder-port "$PORT2" \
        --decoder-init-port "$init" \
        --decoder-alloc-port "$alloc" \
        --proxy-port "$proxy" \
        > "/tmp/build_${BUILD_ID}_${cfg_name}_proxy.log" 2>&1 &
    sleep 10
}

run_p2p_lmcache() {
    local docker1="$1"
    local vllm1="$2"
    local docker2="$3"
    local vllm2="$4"
    local cfg_name="$5"
    LOGFILE1="/tmp/build_${BUILD_ID}_${cfg_name}1.log"
    LOGFILE2="/tmp/build_${BUILD_ID}_${cfg_name}2.log"

    ########## Instance 1 ##########
    # docker args
    docker1_args=(
        --runtime nvidia
        --network host
        --gpus "device=0"
        --volume ~/.cache/huggingface:/root/.cache/huggingface
        --env VLLM_USE_FLASHINFER_SAMPLER=0
        --env HF_TOKEN="$HF_TOKEN"
        --env UCX_TLS=tcp
        --ipc host
        --shm-size 4G
    )
    while IFS= read -r e; do
        [[ -n $e ]] && docker1_args+=(--env "$e")
    done < <(yq -r '.env[]?' <<<"$docker1")
    pull=$(yq -er '."pull-port"' <<<"$docker1" 2>/dev/null)
    docker1_args+=(--env "LMCACHE_CONTROLLER_PULL_URL=localhost:$pull")
    reply=$(yq -er '."reply-port"' <<<"$docker1" 2>/dev/null)
    docker1_args+=(--env "LMCACHE_CONTROLLER_REPLY_URL=localhost:$reply")

    # vllm args
    vllm1_model="$(yq -r '.model' <<<"$vllm1")"
    mapfile -t vllm1_cli_args < <(yq -r '.args // [] | .[]' <<<"$vllm1")
    cmd_args1=(
        lmcache/vllm-openai:build-latest
        "$vllm1_model"
    )
    cmd_args1+=("${vllm1_cli_args[@]}")
    cmd_args1+=("--port" "$PORT1")

    ##### Controller part start #####
    if [ ! -d ".venv" ]; then
        UV_PYTHON=python3 uv -q venv
    fi
    source .venv/bin/activate
    uv pip install -r "$ORIG_DIR/requirements/build.txt" > /dev/null 2>&1
    uv pip install torch==2.7.1 httpx fastapi uvicorn > /dev/null 2>&1
    uv pip install -e "$ORIG_DIR" --no-build-isolation > /dev/null 2>&1
    # Start controller
    PYTHONHASHSEED=123 lmcache_controller \
        --host localhost \
        --port "$PORT" \
        --monitor-ports "{\"pull\": ${pull}, \"reply\": ${reply}}" \
        > "/tmp/build_${BUILD_ID}_${cfg_name}_controller.log" 2>&1 &
    sleep 10
    ##### Controller part end #####

    # Start docker
    CID1=$(
        docker run -d \
            "${docker1_args[@]}" \
            "${cmd_args1[@]}"
    )

    # Health check
    wait_for_openai_api_server "$PORT1" "$vllm1_model" "$CID1"

    # Logging
    touch "$LOGFILE1"
    docker logs -f "$CID1" >>"$LOGFILE1" 2>&1 &

    ########## Instance 2 ##########
    # docker args
    docker2_args=(
        --runtime nvidia
        --network host
        --gpus "device=1"
        --volume ~/.cache/huggingface:/root/.cache/huggingface
        --env VLLM_USE_FLASHINFER_SAMPLER=0
        --env HF_TOKEN="$HF_TOKEN"
        --env UCX_TLS=tcp
        --ipc host
        --shm-size 4G
    )
    while IFS= read -r e; do
        [[ -n $e ]] && docker2_args+=(--env "$e")
    done < <(yq -r '.env[]?' <<<"$docker2")
    pull=$(yq -er '."pull-port"' <<<"$docker2" 2>/dev/null)
    docker2_args+=(--env "LMCACHE_CONTROLLER_PULL_URL=localhost:$pull")
    reply=$(yq -er '."reply-port"' <<<"$docker2" 2>/dev/null)
    docker2_args+=(--env "LMCACHE_CONTROLLER_REPLY_URL=localhost:$reply")

    # vllm args
    vllm2_model="$(yq -r '.model' <<<"$vllm2")"
    mapfile -t vllm2_cli_args < <(yq -r '.args // [] | .[]' <<<"$vllm2")
    cmd_args2=(
        lmcache/vllm-openai:build-latest
        "$vllm2_model"
    )
    cmd_args2+=("${vllm2_cli_args[@]}")
    cmd_args2+=("--port" "$PORT2")

    # Start docker
    CID2=$(
        docker run -d \
            "${docker2_args[@]}" \
            "${cmd_args2[@]}"
    )

    # Health check
    wait_for_openai_api_server "$PORT2" "$vllm2_model" "$CID2"

    # Logging
    touch "$LOGFILE2"
    docker logs -f "$CID2" >>"$LOGFILE2" 2>&1 &
}

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo " "
    echo "Options:"
    echo "  --hf-token|-hft              HuggingFace access token for downloading model(s)"
    echo "  --server-wait-timeout|-swt   Wait time in seconds for vLLM OpenAI server to start"
    echo "  --help|-h                    Print usage"
    echo "  --configs|-c                 Path to a file containing one config filename per line (required)"
    echo "  --tests|-t                   Test mode"
}

#########
# TESTS #
#########

test_vllmopenai_server_with_lmcache_integrated() {
    local model="$1"

    http_status_code=$(
        curl --max-time 60 http://localhost:${PORT}/v1/completions \
            -w "%{http_code}" -o response-file.txt \
            -H "Content-Type: application/json" \
            -d '{
                "model": "'"$model"'",
                "prompt": "<|begin_of_text|><|system|>\nYou are a helpful AI assistant.\n<|user|>\nWhat is the capital of France?\n<|assistant|>",
                "max_tokens": 100,
                "temperature": 0.7
            }'
    )

    if [ "$http_status_code" -ne 200 ]; then
        echo "Model prompt request from OpenAI API server failed, HTTP status code: ${http_status_code}."
        cat response-file.txt
        docker logs -n 20 $CID
        return 1
    else
        echo "Model prompt request from OpenAI API server succeeded"
        cat response-file.txt
    fi
}

run_long_doc_qa() {
    local workload_config="$1"
    local port="$2"

    echo "→ Running long_doc_qa with customed workload config:"
    printf '%s\n' "$workload_config"

    local workload_args=()
    mapfile -d '' -t workload_args < <(
    jq -j '
        to_entries[]
        | select(.value != null and (.value|tostring) != "")
        | (
            if (.value|type) == "boolean" then
            if .value then ["--\(.key)", "\u0000"] else [] end
            elif (.value|type) == "array" then
            .value[]
            | ["--\(.key)", "\u0000",
                (if (type=="string") then . else tostring end),
                "\u0000"]
            else
            ["--\(.key)", "\u0000",
            (if ((.value|type)=="string") then .value else (.value|tostring) end),
            "\u0000"]
            end
        )
        | .[]
    ' <<<"$workload_config"
    )

    if [ ! -d ".venv" ]; then
        UV_PYTHON=python3 uv -q venv
    fi
    source .venv/bin/activate
    uv -q pip install openai pandas matplotlib
    python3 "$ORIG_DIR/benchmarks/long_doc_qa/long_doc_qa.py" \
        "${workload_args[@]}" \
        --port="$port" \
        --output="response.txt"
}

#########
# SETUP #
#########

while [ $# -gt 0 ]; do
    case "$1" in
    --configs* | -c*)
        if [[ "$1" != *=* ]]; then shift; fi
        configs_arg="${1#*=}"
        ;;
    --hf-token* | -hft*)
        if [[ "$1" != *=* ]]; then shift; fi
        HF_TOKEN="${1#*=}"
        ;;
    --server-wait-timeout* | -swt*)
        if [[ "$1" != *=* ]]; then shift; fi
        SERVER_WAIT_TIMEOUT="${1#*=}"
        if ! [[ "$SERVER_WAIT_TIMEOUT" =~ ^[0-9]+$ ]]; then
            echo "server-wait-timeout is wait time in seconds - integer only"
            exit 1
        fi
        ;;
    --help | -h)
        usage
        exit 0
        ;;
    *)
        printf >&2 "Error: Invalid argument\n"
        usage
        exit 1
        ;;
    esac
    shift
done

ORIG_DIR="$PWD"
CONFIG_DIR="${ORIG_DIR}/.buildkite/configs"

# Read the configs argument (always a file with one config per line)
if [[ ! -f "$configs_arg" ]]; then
    echo "Error: --configs file not found: $configs_arg" >&2
    exit 1
fi
mapfile -t CONFIG_NAMES < <(
    sed 's/[[:space:]]\+$//' "$configs_arg"
)

# Find an available port starting from 8000
PORT=$(find_available_port 8000)
if [ $? -ne 0 ]; then
    echo "Failed to find an available port"
    exit 1
fi
echo "Using port $PORT to send or receive requests."

# Need to run from docker directory
cd docker/

# Create the container image
build_lmcache_vllmopenai_image

########
# MAIN #
########

for cfg_name in "${CONFIG_NAMES[@]}"; do
    echo -e "\033[1;33m===== Testing LMCache with ${cfg_name} =====\033[0m"
    cfg_file="${CONFIG_DIR}/${cfg_name}"

    # Start engine
    feature_type=$(yq -r '.feature.type // ""' "$cfg_file")
    if [[ "$feature_type" == "pd" ]]; then
        PORT1=$(find_available_port 8100)
        prefiller_docker_args="$(yq '.["docker-prefiller"]' "$cfg_file")"
        prefiller_vllm_args="$(yq '.["vllm-prefiller"]' "$cfg_file")"
        PORT2=$(find_available_port 8200)
        decoder_docker_args="$(yq '.["docker-decoder"]' "$cfg_file")"
        decoder_vllm_args="$(yq '.["vllm-decoder"]' "$cfg_file")"
        run_pd_lmcache "$prefiller_docker_args" "$prefiller_vllm_args" "$decoder_docker_args" "$decoder_vllm_args" "$cfg_name" 
        model="$(yq -r '.["vllm-prefiller"].model' "$cfg_file")"
    elif [[ "$feature_type" == "p2p" ]]; then
        PORT1=$(find_available_port 8177)
        docker1_args="$(yq '.["docker1"]' "$cfg_file")"
        vllm1_args="$(yq '.["vllm1"]' "$cfg_file")"
        PORT2=$(find_available_port 8277)
        docker2_args="$(yq '.["docker2"]' "$cfg_file")"
        vllm2_args="$(yq '.["vllm2"]' "$cfg_file")"
        run_p2p_lmcache "$docker1_args" "$vllm1_args" "$docker2_args" "$vllm2_args" "$cfg_name" 
        model="$(yq -r '.["vllm1"].model' "$cfg_file")"
    elif [[ -z "$feature_type" ]]; then
        docker_args="$(yq '.docker' "$cfg_file")"
        vllm_args="$(yq '.vllm' "$cfg_file")"
        run_lmcache_vllmopenai_container "$docker_args" "$vllm_args" "$cfg_name"
        model="$(yq -r '.vllm.model' "$cfg_file")"
    fi
    
    # Send request
    test_mode="$(yq -r '.workload.type' "$cfg_file")"
    if [ "$test_mode" = "dummy" ]; then
        test_vllmopenai_server_with_lmcache_integrated "$model"
    elif [ "$test_mode" = "long_doc_qa" ]; then
        workload_yaml="$(yq "(.workload * {\"model\": \"$model\"}) | del(.type)" "$cfg_file")"
        if [[ "$feature_type" == "p2p" ]]; then
            tmp_workload_yaml=$(jq 'del(."expected-latency")' <<< "$workload_yaml")
            run_long_doc_qa "$tmp_workload_yaml" "$PORT1"
            run_long_doc_qa "$workload_yaml" "$PORT2"
        else
            run_long_doc_qa "$workload_yaml" "$PORT"
        fi
    fi

    cleanup 0
done

exit 0
