# SPDX-License-Identifier: Apache-2.0
# Standard
from typing import TYPE_CHECKING, Optional, Union

# First Party
from lmcache.logging import init_logger
from lmcache.v1.cache_engine import LMCacheEngine
from lmcache.v1.config import LMCacheEngineConfig
from lmcache.v1.lookup_client.abstract_client import LookupClientInterface
from lmcache.v1.lookup_client.hit_limit_lookup_client import HitLimitLookupClient
from lmcache.v1.lookup_client.mooncake_lookup_client import MooncakeLookupClient

if TYPE_CHECKING:
    # Third Party
    from vllm.config import VllmConfig

    # First Party
    from lmcache.v1.lookup_client.lmcache_async_lookup_client import (
        LMCacheAsyncLookupServer,
    )
    from lmcache.v1.lookup_client.lmcache_lookup_client import LMCacheLookupServer

logger = init_logger(__name__)


class LookupClientFactory:
    """Factory for creating lookup clients and servers based on configuration."""

    @staticmethod
    def create_lookup_client(
        vllm_config: "VllmConfig",
        config: LMCacheEngineConfig,
    ) -> LookupClientInterface:
        """
        Create a lookup client based on the configuration.

        Args:
            vllm_config: The vLLM configuration
            config: The LMCache engine configuration

        Returns:
            A lookup client instance
        """

        # Check if external_lookup_client is configured
        if config.external_lookup_client is not None:
            if config.enable_async_loading:
                raise ValueError(
                    "Asynchronous loading is not supported for external lookup clients."
                )
            client = LookupClientFactory._create_external_lookup_client(
                config.external_lookup_client, vllm_config
            )
        else:
            # First Party
            from lmcache.v1.lookup_client.lmcache_async_lookup_client import (
                LMCacheAsyncLookupClient,
            )
            from lmcache.v1.lookup_client.lmcache_lookup_client import (
                LMCacheLookupClient,
            )

            if config.enable_async_loading:
                client = LMCacheAsyncLookupClient(vllm_config)
            else:
                client = LMCacheLookupClient(vllm_config)

        if config.hit_miss_ratio is not None and 0 <= config.hit_miss_ratio <= 1:
            return HitLimitLookupClient(client, config)
        return client

    @staticmethod
    def create_lookup_server(
        lmcache_engine: LMCacheEngine,
        vllm_config: "VllmConfig",
    ) -> Optional[Union["LMCacheLookupServer", "LMCacheAsyncLookupServer"]]:
        """
        Create a lookup server based on the configuration.

        Args:
            lmcache_engine: The LMCache engine instance
            vllm_config: The vLLM configuration

        Returns:
            A lookup server instance, or None if no server should be created
        """
        config = lmcache_engine.config
        assert isinstance(config, LMCacheEngineConfig), (
            "LMCache v1 config is expected for lookup server and client"
        )

        mla_lookup_server_worker_id = config.get_mla_lookup_server_worker_id(
            lmcache_engine.metadata.use_mla
        )
        assert mla_lookup_server_worker_id < lmcache_engine.metadata.world_size

        if config.external_lookup_client is None and (
            mla_lookup_server_worker_id < 0
            or lmcache_engine.metadata.worker_id == mla_lookup_server_worker_id
        ):
            # First Party
            from lmcache.v1.lookup_client.lmcache_async_lookup_client import (
                LMCacheAsyncLookupServer,
            )
            from lmcache.v1.lookup_client.lmcache_lookup_client import (
                LMCacheLookupServer,
            )

            if config.enable_async_loading:
                return LMCacheAsyncLookupServer(lmcache_engine, vllm_config)
            else:
                return LMCacheLookupServer(lmcache_engine, vllm_config)

        return None

    @staticmethod
    def _create_external_lookup_client(
        external_lookup_uri: str,
        vllm_config: "VllmConfig",
    ) -> LookupClientInterface:
        """
        Create an external lookup client based on the URI format.

        Args:
            external_lookup_uri: URI in format <scheme>://<address>
            vllm_config: The vLLM configuration

        Returns:
            A lookup client instance

        Raises:
            ValueError: If the URI format is unsupported
        """
        # Parse URI scheme and address
        if "://" not in external_lookup_uri:
            raise ValueError(
                f"Invalid external lookup client URI format: {external_lookup_uri}. "
                "Expected format: <scheme>://<address>"
            )

        scheme, address = external_lookup_uri.split("://", 1)

        # Route to appropriate client based on scheme
        if scheme == "mooncakestore":
            return LookupClientFactory._create_mooncake_lookup_client(
                address, vllm_config
            )
        else:
            raise ValueError(
                f"Unsupported external lookup client scheme: {scheme}. "
                "Supported schemes: mooncakestore"
            )

    @staticmethod
    def _create_mooncake_lookup_client(
        master_address: str,
        vllm_config: "VllmConfig",
    ) -> "MooncakeLookupClient":
        """Create a MooncakeLookupClient instance."""
        # First Party
        from lmcache.v1.lookup_client.mooncake_lookup_client import (
            MooncakeLookupClient,
        )

        return MooncakeLookupClient(vllm_config, master_address)
