## Example of Disaggregated Prefill in vLLM v1

This example demonstrates how to run LMCache with disaggregated prefill using NIXL on a single node.

### Prerequisites

- Install [LMCache](https://github.com/LMCache/LMCache). You can simply run `pip install lmcache`.
- Install [NIXL](https://github.com/ai-dynamo/nixl).
- At least 4 GPUs
- Valid Hugging Face token (HF_TOKEN) for Llama 3.1 8B Instruct.

### Usage

Run
```bash
bash disagg_example_xpyd.sh
```

to start disaggregated prefill and benchmark the performance.

The script will:

1. Launch 2 decoder instances listening on port 7200 and 7201, respectively
2. Launch 2 prefill instances listening on ports 7100 and 7101, respectively
3. Launch a proxy server that uses round-robin to distribute requests between the prefill instances and decode instances, listening on port 9100

Press `Ctrl+C` to stop the servers.

### Advanced Configuration

#### Multi-Host Support

The proxy server supports CSV format for specifying multiple hosts and ports for both prefillers and decoders. This enables flexible deployment across multiple machines:

```bash
# Multi-machine deployment
python disagg_proxy_server.py \
    --prefiller-host "${host1-IP},${host2-IP}" \
    --prefiller-port "8000" \
    --decoder-host "${host3-IP},${host4-IP}" \
    --decoder-port "8000,8001"

# Above example `--prefiller-port "8000"` means the host1 and host2 vLLM instances both use port 8000 for model serving.
# Above example `--decoder-port "8000,8001"` means host3 uses port 8000 and host4 uses 8001 for model serving. (Using different ports on different hosts is not required, but demonstrates argument flexibility)
```

#### To support Tensor-Parallel

In Decoder's lmcache configuration file, different ports are required for different TP ranks. The below example shows a TP=8 case with 8 ports (to support vLLM instance with `--tensor-parallel-size 8`)

```yaml
nixl_peer_init_port:  [7300,7301,7302,7303,7304,7305,7306,7307]
nixl_peer_alloc_port: [7400,7401,7402,7403,7404,7405,7406,7407]
```

Accordingly, the `disagg_proxy_server.py` should use the same ports aligning with decoder configuration:
```bash
python disagg_proxy_server.py \
    .... \ # other arguments
    --decoder-init-port  "7300,7301,7302,7303,7304,7305,7306,7307" \
    --decoder-alloc-port "7400,7401,7402,7403,7404,7405,7406,7407"
```
#### Example benchmark command

If you have vLLM [benchmark_serving.py](https://github.com/vllm-project/vllm/blob/main/benchmarks/benchmark_serving.py), you can run the following command to benchmark the serving performance of the disaggregated prefill setup:

```bash
vllm bench serve --port 9100 --seed $(date +%s) \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --dataset-name random --random-input-len 7500 --random-output-len 200 \
    --num-prompts 30 --burstiness 100 --request-rate 1 --ignore-eos
```

Expected output from the benchmark script:

```plaintext
============ Serving Benchmark Result ============
Successful requests:                     30
Benchmark duration (s):                  31.34
Total input tokens:                      224970
Total generated tokens:                  6000
Request throughput (req/s):              0.96
Output token throughput (tok/s):         191.44
Total Token throughput (tok/s):          7369.36
---------------Time to First Token----------------
Mean TTFT (ms):                          313.41
Median TTFT (ms):                        272.83
P99 TTFT (ms):                           837.32
-----Time per Output Token (excl. 1st token)------
Mean TPOT (ms):                          8.84
Median TPOT (ms):                        8.72
P99 TPOT (ms):                           11.35
---------------Inter-token Latency----------------
Mean ITL (ms):                           8.84
Median ITL (ms):                         8.61
P99 ITL (ms):                            11.43
==================================================
```

### Components

#### Server Scripts
- `disagg_vllm_launcher.sh` - Launches individual vLLM servers for prefill/decode, and also launches the proxy server.
- `disagg_proxy_server.py` - FastAPI proxy server that coordinates between prefiller and decoder
- `disagg_example_xpyd.sh` - Main script to run the example

#### Configuration
- `configs/lmcache-prefiller-config.yaml` - Configuration for prefiller server
- `configs/lmcache-decoder-1-config.yaml` - Configuration for decoder server 1
- `configs/lmcache-decoder-2-config.yaml` - Configuration for decoder server 2

#### Log Files
The main script generates several log files:
- `prefiller1.log` and `prefiller2.log` - Logs from the prefill servers
- `decoder1.log` and `decoder2.log` - Logs from the decode server
- `proxy.log` - Logs from the proxy server
