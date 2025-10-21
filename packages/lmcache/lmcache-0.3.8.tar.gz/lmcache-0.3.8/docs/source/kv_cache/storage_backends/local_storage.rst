Local storage
=============

.. _local-storage-overview:

Overview
--------

CPU RAM and Local Storage are the two ways of offloading KV cache onto non-GPU
memory of the same machine that is running inference.


Two ways to configure LMCache Disk Offloading:
----------------------------------------------


**1. Environment Variables:**

``LMCACHE_USE_EXPERIMENTAL`` MUST be set by environment variable directly.

.. code-block:: bash

    # 256 Tokens per KV Chunk
    export LMCACHE_CHUNK_SIZE=256
    # None if disabled
    # Otherwise, enable by setting the directory where LMCache will
    # create files for each KV cache chunks
    # (this directory does NOT need to exist beforehand)
    export LMCACHE_LOCAL_DISK="file://local/disk_test/local_disk/"
    # 5GB of Disk
    export LMCACHE_MAX_LOCAL_DISK_SIZE=5.0

    # Disable page cache
    # This should be turned on for better performance if most local CPU memory is used
    export LMCACHE_EXTRA_CONFIG='{'use_odirect': True}'

**2. Configuration File**:

Passed in through ``LMCACHE_CONFIG_FILE=your-lmcache-config.yaml``

``LMCACHE_USE_EXPERIMENTAL`` MUST be set by environment variable directly.

.. code-block:: yaml

    # 256 Tokens per KV Chunk
    chunk_size: 256
    # Enable Disk backend
    local_disk: "file://local/disk_test/local_disk/"
    # 5GB of Disk memory
    max_local_disk_size: 5.0

    # Disable page cache
    # This should be turned on for better performance if most local CPU memory is used
    extra_config: {'use_odirect': True}

Local Storage Explanation:
--------------------------

Unlike CPU RAM offloading, disk offloading is *disabled* by default (``local_disk`` is set to ``None``) and the
max local disk size is set to 0GB instead of 5GB like the default max local cpu size
since the disk space is not strictly necessary for LMCache to function.

Furthermore, instead of greedily allocating the max space up front like the pinned CPU RAM, the disk backend will
create one file per KV cache chunk as they are stored, evicting if capacity is exceeded (LRU currently).

The disk and remote (see :doc:`Redis <./redis>`, :doc:`Mooncake <./mooncake>`, :doc:`Valkey <./valkey>`, :doc:`InfiniStore <./infinistore>`)
backends have asynchronous put() operations so that the IO latency will not slow down inference in addition to blocking get() operations.
The local disk backend also has a prefetch() operation that will preemptively move KV caches from the disk to CPU RAM offloading storage
(i.e. ``LMCACHE_LOCAL_CPU=True`` should be set, see :doc:`CPU RAM <./cpu_ram>`) for specified tokens (these KV caches are also still kept in the disk).

.. _local-storage-online-inference-example:

Online Inference Example
------------------------

This example is almost identical to the :doc:`CPU RAM <./cpu_ram>` example.

Let's feel the TTFT (time to first token) differential!

.. _local-storage-prerequisites:

**Prerequisites:**

- A Machine with at least one GPU. Adjust the max model length of your vllm instance depending on your GPU memory and the long context you want to use.

- vllm and lmcache installed (:doc:`Installation Guide <../../getting_started/installation>`)

- Hugging Face access to ``meta-llama/Meta-Llama-3.1-8B-Instruct``

.. code-block:: bash

    export HF_TOKEN=your_hugging_face_token

- A few packages:

.. code-block:: bash

    pip install openai transformers



**Step 0. Set up a directory for this example:**

.. code-block:: bash

    mkdir lmcache-local-disk-example
    cd lmcache-local-disk-example

**Step 1. Prepare a long context!**

We want a context long enough that vllm's prefix caching will not be able to hold the KV caches in
GPU memory and LMCache is necessary to keep KV caches in non-GPU memory:

.. code-block:: bash

    # 382757 bytes
    man bash > man-bash.txt

**Step 2. Start a vLLM server with Disk offloading enabled:**

*Generally, it is not recommended but we will disable CPU offloading to feel just the disk offloading latency.*

Create a an lmcache configuration file called: ``disk-offload.yaml``

Example ``config.yaml``:

.. code-block:: yaml

    chunk_size: 256
    local_cpu: false
    max_local_cpu_size: 5.0
    local_disk: "file://local/disk_test/local_disk/"
    max_local_disk_size: 5.0

If you don't want to use a config file, uncomment the first five environment variables
and then comment out the ``LMCACHE_CONFIG_FILE`` below:

.. code-block:: bash

    # LMCACHE_CHUNK_SIZE=256 \
    # LMCACHE_LOCAL_CPU=False \
    # LMCACHE_MAX_LOCAL_CPU_SIZE=5.0 \
    # LMCACHE_LOCAL_DISK="file://local/disk_test/local_disk/" \
    # LMCACHE_MAX_LOCAL_DISK_SIZE=5.0 \
    LMCACHE_CONFIG_FILE="disk-offload.yaml" \
    LMCACHE_USE_EXPERIMENTAL=True \
    vllm serve \
        meta-llama/Llama-3.1-8B-Instruct \
        --max-model-len 16384 \
        --kv-transfer-config \
        '{"kv_connector":"LMCacheConnectorV1", "kv_role":"kv_both"}'

- ``--kv-transfer-config``: This is the parameter that actually tells vLLM to use LMCache for KV cache offloading.
    - ``kv_connector``: Specifies the LMCache connector for vLLM V1
    - ``kv_role``: Set to "kv_both" for both storing and loading KV cache (important because we will run two queries and the first will produce/store a KV cache while the second will consume/load that KV cache)


**Step 3. Query TTFT improvements with LMCache:**

Once the Open AI compatible server is running on default vllm port 8000, let's query it twice with the same long context!

Create a script called ``query-twice.py`` and paste the following code:

.. code-block:: python

    import time
    from openai import OpenAI
    from transformers import AutoTokenizer

    client = OpenAI(
        api_key="dummy-key",  # required by OpenAI client even for local servers
        base_url="http://localhost:8000/v1"
    )

    models = client.models.list()
    model = models.data[0].id

    # 119512 characters total
    # 26054 tokens total
    long_context = ""
    with open("man-bash.txt", "r") as f:
        long_context = f.read()

    # a truncation of the long context for the --max-model-len 16384
    # if you increase the --max-model-len, you can decrease the truncation i.e.
    # use more of the long context
    long_context = long_context[:70000]

    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3.1-8B-Instruct")
    question = "Summarize bash in 2 sentences."

    prompt = f"{long_context}\n\n{question}"

    print(f"Number of tokens in prompt: {len(tokenizer.encode(prompt))}")

    def query_and_measure_ttft():
        start = time.perf_counter()
        ttft = None

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            temperature=0.7,
            stream=True,
        )

        for chunk in chat_completion:
            chunk_message = chunk.choices[0].delta.content
            if chunk_message is not None:
                if ttft is None:
                    ttft = time.perf_counter()
                print(chunk_message, end="", flush=True)

        print("\n")  # New line after streaming
        return ttft - start

    print("Querying vLLM server with cold LMCache Disk Offload")
    cold_ttft = query_and_measure_ttft()
    print(f"Cold TTFT: {cold_ttft:.3f} seconds")

    print("\nQuerying vLLM server with warm LMCache Disk Offload")
    warm_ttft = query_and_measure_ttft()
    print(f"Warm TTFT: {warm_ttft:.3f} seconds")

    print(f"\nTTFT Improvement: {(cold_ttft - warm_ttft):.3f} seconds \
        ({(cold_ttft/warm_ttft):.1f}x faster)")

Then run:

.. code-block:: bash

    python query-twice.py

Since we're in streaming mode, you'll be able to feel the TTFT differential in
real time!

Note that if we were to enable ``LMCACHE_LOCAL_CPU=True``, we would just be using
the same example from :doc:`CPU RAM <./cpu_ram>` since the CPU RAM is checked before
the disk by LMCache. In practice, the disk will be capable of storing a larger
quantity of KV caches so the CPU RAM offloading will only be able to store a
subset of the disk's KV caches.

**Example Output:**


.. code-block:: text

    Number of tokens in prompt: 15376
    Querying vLLM server with cold LMCache Disk Offload
    Bash is a Unix shell and command-line interpreter that reads and executes
    commands from standard input or a file, incorporating features from the
    Korn and C shells. It is a conformant implementation of the IEEE POSIX
    specification and can be configure to be POSIX-conformant by default,
    supporting a wide range of options, built-in commands,
    and features for scripting, job control, and interactive use.

    Cold TTFT: 6.314 seconds

    Querying vLLM server with warm LMCache Disk Offload
    Bash is a Unix shell and command-line interpreter that reads and
    executes commands from the standard input or a file, and is designed
    to be a conformant implementation of the IEEE POSIX specification. It
    is a powerful tool for automating tasks, managing files and directories,
    and interacting with other programs and services, with features such as
    scripting, conditional statements, loops, and functions.

    Warm TTFT: 0.148 seconds

TTFT Improvement: 6.166 seconds     (42.6x faster)

If you look at the logs of your vLLM server, you should see (the logs are truncated for cleanliness):

.. code-block:: text

    # Cold LMCache Miss and then Store

    LMCache INFO: Reqid: chatcmpl-8676f9b9ebf04c79a5d47b9ada7b65fd, Total tokens 15410,
    LMCache hit tokens: 0, need to load: 0

    # you should see 8 of these storing logs total
    # 2048 tokens is a multiple of the chunk size
    LMCache INFO: Storing KV cache for 2048 out of 12288 tokens for request
    chatcmpl-8676f9b9ebf04c79a5d47b9ada7b65fd

    LMCache INFO: Storing KV cache for 2048 out of 14336 tokens for request
    chatcmpl-8676f9b9ebf04c79a5d47b9ada7b65fd

    LMCache INFO: Storing KV cache for 1074 out of 15410 tokens for request
    chatcmpl-8676f9b9ebf04c79a5d47b9ada7b65fd

    # Warm LMCache Hit!!

    LMCache INFO: Reqid: chatcmpl-136d9dac1ba94bd4b4ae85007e8ad437, Total tokens 15410,
    LMCache hit tokens: 15409, need to load: 1


.. _local-storage-tips:

Tips:
-----

- If you want to run the ``query-twice.py`` script multiple times, you'll need to either restart the vLLM LMCache server or change the prefix of the context you pass in since you've already warmed LMCache.

- The max model length here was decided by running an L4 with only 23GB of GPU memory. If you have more memory, you can increase the max model length and modify ``query-twice.py`` to use more of the long context. LMCache TTFT improvement becomes more pronounced as the context length increases!