
Nixl
====

.. _nixl-overview:

Overview
--------

NIXL (NVIDIA Inference Xfer Library) is a high-performance library designed for accelerating point to point communications in AI inference frameworks. It provides an abstraction over various types of memory (CPU and GPU) and storage through a modular plug-in architecture, enabling efficient data transfer and coordination between different components of the inference pipeline.

LMCache supports using NIXL as a storage backend, allowing using NIXL to save either GPU or CPU memory into storage.

Prerequisites
~~~~~~~~~~~~~

- **LMCache**: Install with ``pip install lmcache``
- **NIXL**: Install from `NIXL GitHub repository <https://github.com/ai-dynamo/nixl>`_
- **Model Access**: Valid Hugging Face token (HF_TOKEN) for Llama 3.1 8B Instruct

Ways to configure LMCache NIXL Offloading
-----------------------------------------

**Configuration File**:

Passed in through ``LMCACHE_CONFIG_FILE=lmcache-config.yaml``

``LMCACHE_USE_EXPERIMENTAL`` MUST be set.

Example ``lmcache-config.yaml`` for POSIX backend:

.. code-block:: yaml

    chunk_size: 256
    nixl_buffer_size: 1073741824 # 1GB
    nixl_buffer_device: cpu
    extra_config:
      enable_nixl_storage: true
      nixl_backend: POSIX
      nixl_pool_size: 64
      nixl_path: /mnt/nixl/cache/

Key settings:

- ``nixl_buffer_size``: buffer size for NIXL transfers.

- ``nixl_pool_size``: number of descriptors opened at init time for nixl backend.

- ``nixl_path``: directory under which the storage files will be saved (e.g. /mnt/nixl/). Needed for NIXL backends that store to file.

- ``nixl_buffer_device``: dictates where the memory managed by NIXL should be on. "cpu" or "cuda" is supported for "GDS" and "GDS_MT" backends - for "POSIX", "HF3FS" & "OBJ", must be "cpu".

- ``nixl_backend``: configuration of which nixl backend to use for storage.

  .. note::

    Supported backends are: ["GDS", "GDS_MT", "POSIX", "HF3FS", "OBJ"].

    Backend specific params should be provided via ``extra_config.nixl_backend_params``. Please refer to NIXL documentation for specifics.

Example ``lmcache-config.yaml`` for OBJ backend using S3 API:

.. code-block:: yaml

    chunk_size: 256
    nixl_buffer_size: 1073741824 # 1GB
    nixl_buffer_device: cpu
    extra_config:
      enable_nixl_storage: true
      nixl_backend: OBJ
      nixl_pool_size: 64
      nixl_path: /mnt/nixl/cache/
      nixl_backend_params:
        access_key: <your_access_key>
        secret_key: <your_secret_key>
        bucket: <your_bucket>
        region: <your_region>
