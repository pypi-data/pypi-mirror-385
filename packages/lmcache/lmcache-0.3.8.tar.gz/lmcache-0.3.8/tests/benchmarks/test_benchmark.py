# SPDX-License-Identifier: Apache-2.0
# Standard
from functools import partial
import os
import random
import shlex
import subprocess
import tempfile
import time

# Third Party
import pytest
import torch

# First Party
from lmcache.utils import mock_up_broadcast_fn, mock_up_broadcast_object_fn
from lmcache.v1.cache_engine import LMCacheEngineBuilder
from lmcache.v1.config import LMCacheEngineConfig
from tests.v1.utils import (
    create_gpu_connector,
    dumb_metadata,
    generate_kv_cache_paged_list_tensors,
    generate_tokens,
)


# helper functions
def generate_random_slot_mapping(num_blocks, block_size, num_tokens, device):
    slot_mapping = random.sample(range(0, num_blocks * block_size), num_tokens)
    return torch.tensor(slot_mapping, device=device)


@pytest.fixture
def create_config():
    """
    backend can be:
    - cpu
    - disk
    - fsconnector
    """

    def make_config(backend, size, **kwargs):
        match backend:
            case "cpu":
                return LMCacheEngineConfig.from_defaults(
                    local_cpu=True,
                    max_local_cpu_size=size,
                    extra_config={"force_store_wait": False},
                )
            case "disk":
                assert "path" in kwargs, "'path' is missing for disk backend"
                return LMCacheEngineConfig.from_defaults(
                    local_cpu=False,
                    max_local_cpu_size=size,
                    local_disk=kwargs["path"],
                    max_local_disk_size=size,
                    extra_config={"force_store_wait": False},
                )
            case "fsconnector":
                assert "path" in kwargs, "'path' is missing for fsconnector"
                p = kwargs["path"]
                return LMCacheEngineConfig.from_defaults(
                    local_cpu=False,
                    max_local_cpu_size=size,
                    remote_url=f"fs://host:0/{p}/",
                    remote_serde="naive",
                    extra_config={"force_store_wait": False},
                )
            case _:
                print(f"Error: unknown backend: {backend}")
                print("Supported backends: 'cpu', 'disk', and 'fsconnector'")
                raise ValueError(f"Unknown backend: {backend}")

    homedir = os.environ.get("HOME", "/tmp")
    with tempfile.TemporaryDirectory(
        dir=homedir, ignore_cleanup_errors=True
    ) as temp_dir:
        print("Temp dir is:", temp_dir)
        yield partial(make_config, path=temp_dir)


# test store 10GB data (1GB * 10)
@pytest.mark.no_shared_allocator
@pytest.mark.benchmark(group="store")
@pytest.mark.parametrize("backend", ["cpu", "disk", "fsconnector"])
@pytest.mark.skipif(
    not torch.cuda.is_available(),
    reason="TODO: Add non-CUDA implementation to VLLMPagedMemGPUConnectorV2",
)
def test_store_1GB(benchmark, backend, create_config, autorelease_v1):
    """
    In this test, it will run engine.store to store 10GB data in total.
    The configs are carefully tuned to have:
    - Each request has 2K tokens and 0.25GB KV cache
    - There will be 40 store requests (storing 10GB data) in total.
    - The store requests are split into 10 rounds, where each round has
    1GB data.
    - The benchmark tool will measure the time for each round (time to
    store 1GB)

    When creating the LMCache engine, it will first create a 1.5GB buffer, so
    there will be eviction starting from the second round.

    At the end of each round, we will run `engine.lookup` to ensure that all
    the data are successfully stored into the LMCache engine. The test will
    measure the time for each round and calculate the average time across
    the rounds.

    pytest-benchmark will report the average time. To calculate the store
    throughput, we can use 1GB / average_round_time.
    """
    # model-related metadatas
    num_heads = 8
    head_dim = 128
    num_layers = 32
    dtype = torch.bfloat16

    # lmcache and vllm configs
    device = "cuda"
    fmt = "vllm"
    num_tokens = 2000

    num_blocks = 1000
    block_size = 16

    chunk_size = 256
    kv_shape = (num_layers, 2, chunk_size, num_heads, head_dim)

    # Test configs
    # - single request has 1.25GB KV, 8 requests has 10GB
    # so we want to do 10 rounds
    num_requests = 4
    num_repeats = 10

    # Initialize related modules
    connector = create_gpu_connector(num_heads * head_dim, num_layers)
    kv_cache = generate_kv_cache_paged_list_tensors(
        num_blocks, device, block_size, dtype
    )

    cache_size = 1.5  # Allocate 15 GB KV cache buffer
    cfg = create_config(backend, cache_size)

    engine = autorelease_v1(
        LMCacheEngineBuilder.get_or_create(
            "test",
            cfg,
            dumb_metadata(fmt, kv_shape),
            connector,
            mock_up_broadcast_fn,
            mock_up_broadcast_object_fn,
        )
    )

    # Run benchmark
    def run_func(tokens, slot_mappings):
        for t, s in zip(tokens, slot_mappings, strict=False):
            engine.store(t, kvcaches=kv_cache, slot_mapping=s)

        # Wait for all tokens are being stored
        timeout = 60
        start = time.time()
        while time.time() - start < timeout:
            ready = all([engine.lookup(t) == len(t) for t in tokens])
            if ready:
                return
            else:
                time.sleep(0.05)
        raise TimeoutError(f"Store operation haven't finished in {timeout} seconds")

    def setup():
        list_tokens = [generate_tokens(num_tokens, device) for _ in range(num_requests)]

        list_slot_mappings = [
            generate_random_slot_mapping(num_blocks, block_size, num_tokens, device)
            for _ in range(num_requests)
        ]
        subprocess.run(shlex.split("rm -rf local/disk_test/local_disk/"))
        return (list_tokens, list_slot_mappings), {}

    benchmark.pedantic(run_func, setup=setup, rounds=num_repeats, iterations=1)


# Test retrieve 10data (10 rounds, each round 1GB, 100% hit)
@pytest.mark.no_shared_allocator
@pytest.mark.benchmark(group="retrieve")
@pytest.mark.parametrize("backend", ["cpu", "disk", "fsconnector"])
@pytest.mark.skipif(
    not torch.cuda.is_available(),
    reason="TODO: Add non-CUDA implementation to VLLMPagedMemGPUConnectorV2",
)
def test_retrieve_1GB_allhit(benchmark, backend, create_config, autorelease_v1):
    """
    In this test, it will run engine.retrieve to retrieve 10GB data in total.
    The configs are carefully tuned to have:
    - Each request has 2K tokens and 0.25GB KV cache
    - There will be 40 retrieve requests (retrieving 10GB data) in total.
    - The retrieve requests are split into 10 rounds, where each round has
    1GB data.
    - The benchmark tool will measure the time for each round (time to
    retrieve 1GB)

    When creating the LMCache engine, it will first create a 1.5GB buffer, and
    then store 4 requests (1GB) into the engine.
    After that, there will be 10 rounds of retrieve, where each round queries
    the same set of requests (but shuffled) with a 100% hit rate.

    The test will measure the time for each round and calculate the average
    time across the rounds.

    pytest-benchmark will report the average time. To calculate the retrieve
    throughput, we can use 1GB / average_round_time.
    """
    # model-related metadatas
    num_heads = 8
    head_dim = 128
    num_layers = 32
    dtype = torch.bfloat16

    # lmcache and vllm configs
    device = "cuda"
    fmt = "vllm"
    num_tokens = 2000

    num_blocks = 1000
    block_size = 16

    chunk_size = 256
    kv_shape = (num_layers, 2, chunk_size, num_heads, head_dim)

    # Test configs
    # - Single request has 1.25 GB KV, 8 requests will use 10GB,
    # so num repeats should be 10 to achieve 100 GB access
    num_requests = 4
    num_repeats = 10

    # Initialize related modules
    connector = create_gpu_connector(num_heads * head_dim, num_layers)
    kv_cache = generate_kv_cache_paged_list_tensors(
        num_blocks, device, block_size, dtype
    )

    list_tokens = [generate_tokens(num_tokens, device) for _ in range(num_requests)]

    list_slot_mappings = [
        generate_random_slot_mapping(num_blocks, block_size, num_tokens, device)
        for _ in range(num_requests)
    ]

    cache_size = 1.5  # 2 GB KV cache buffer
    cfg = create_config(backend, cache_size)

    engine = autorelease_v1(
        LMCacheEngineBuilder.get_or_create(
            "test",
            cfg,
            dumb_metadata(fmt, kv_shape),
            connector,
            mock_up_broadcast_fn,
            mock_up_broadcast_object_fn,
        )
    )

    for t, s in zip(list_tokens, list_slot_mappings, strict=False):
        engine.store(t, kvcaches=kv_cache, slot_mapping=s)

    # Wait for kv cache to be ready
    timeout = 60
    start = time.time()
    ready = False
    while time.time() - start < timeout:
        ready = all([engine.lookup(t) == len(t) for t in list_tokens])
        if ready:
            break
        else:
            time.sleep(0.1)
    assert ready, "Store is not finished in 60 seconds"

    # Run benchmark
    def setup():
        indexes = list(range(len(list_tokens)))
        random.shuffle(indexes)
        return (
            [list_tokens[i] for i in indexes],
            [list_slot_mappings[i] for i in indexes],
        ), {}

    def run_func(tokens, slot_mappings):
        for t, s in zip(tokens, slot_mappings, strict=False):
            engine.retrieve(t, kvcaches=kv_cache, slot_mapping=s)

    benchmark.pedantic(run_func, setup=setup, rounds=num_repeats, iterations=1)


# Test lookup 2K * 10 requests, 100% hit
@pytest.mark.no_shared_allocator
@pytest.mark.benchmark(group="lookup")
@pytest.mark.parametrize("backend", ["cpu", "disk", "fsconnector"])
@pytest.mark.skipif(
    not torch.cuda.is_available(),
    reason="TODO: Add non-CUDA implementation to VLLMPagedMemGPUConnectorV2",
)
def test_lookup_20K_tokens(benchmark, backend, create_config, autorelease_v1):
    """
    In this test, it will run engine.lookup to lookup 200K tokens in total.
    The configs are carefully tuned to have:
    - Each request has 2K tokens and 0.25GB KV cache
    - There will be 100 lookup requests split into 10 rounds.
    - Each round will shuffle the requests.

    When creating the LMCache engine, it will first create a 5GB buffer, and
    then store 10 requests (3GB) into the engine.
    the same set of requests (but shuffled) with a 100% hit rate.

    The test will measure the time for each round and calculate the average
    time across the rounds.

    pytest-benchmark will report the average time. To calculate the lookup
    throughput, we can use 100K tokens / average_round_time.
    """
    # model-related metadatas
    num_heads = 8
    head_dim = 128
    num_layers = 32
    dtype = torch.bfloat16

    # lmcache and vllm configs
    device = "cuda"
    fmt = "vllm"
    num_tokens = 2000

    num_blocks = 1000
    block_size = 16

    chunk_size = 256
    kv_shape = (num_layers, 2, chunk_size, num_heads, head_dim)

    # Test configs
    num_requests = 10
    num_repeats = 10

    # Initialize related modules
    connector = create_gpu_connector(num_heads * head_dim, num_layers)
    kv_cache = generate_kv_cache_paged_list_tensors(
        num_blocks, device, block_size, dtype
    )

    list_tokens = [generate_tokens(num_tokens, device) for _ in range(num_requests)]

    list_slot_mappings = [
        generate_random_slot_mapping(num_blocks, block_size, num_tokens, device)
        for _ in range(num_requests)
    ]

    # TODO: Rewrite the config generation to another helper function
    cache_size = 3  # 15 GB KV cache buffer
    cfg = create_config(backend, cache_size)

    engine = autorelease_v1(
        LMCacheEngineBuilder.get_or_create(
            "test",
            cfg,
            dumb_metadata(fmt, kv_shape),
            connector,
            mock_up_broadcast_fn,
            mock_up_broadcast_object_fn,
        )
    )

    for t, s in zip(list_tokens, list_slot_mappings, strict=False):
        engine.store(t, kvcaches=kv_cache, slot_mapping=s)

    # Make sure all the requests are stored
    timeout = 60
    start = time.time()
    ready = False
    while time.time() - start < timeout:
        ready = all([engine.lookup(t) == len(t) for t in list_tokens])
        if ready:
            break
        else:
            time.sleep(0.1)
    assert ready, "Store is not finished in 60 seconds"

    # Run benchmark
    def setup():
        indexes = list(range(len(list_tokens)))
        random.shuffle(indexes)
        return (
            [list_tokens[i] for i in indexes],
            [list_slot_mappings[i] for i in indexes],
        ), {}

    def run_func(tokens, slot_mappings):
        for t, s in zip(tokens, slot_mappings, strict=False):
            assert engine.lookup(t) == len(t)

    benchmark.pedantic(run_func, setup=setup, rounds=num_repeats, iterations=1)
