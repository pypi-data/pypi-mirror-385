"""D365FO Client Manager for MCP Server.

Manages D365FO client instances and connection pooling for the MCP server.
Provides centralized client management with session reuse and error handling.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Optional

from ..client import FOClient
from ..exceptions import AuthenticationError, FOClientError
from ..models import FOClientConfig
from ..profile_manager import ProfileManager

logger = logging.getLogger(__name__)


class D365FOClientManager:
    """Manages D365FO client instances and connection pooling."""

    def __init__(self, profile_manager: Optional[ProfileManager] = None):
        """Initialize the client manager.

        Args:
            config: Configuration dictionary with client settings
            profile_manager: Optional shared ProfileManager instance
        """
        self._client_pool: Dict[str, FOClient] = {}
        self._session_lock = asyncio.Lock()
        self._last_health_check: Optional[datetime] = None
        self.profile_manager = profile_manager or ProfileManager()

    async def get_client(self, profile: str = "default") -> FOClient:
        """Get or create a client for the specified profile.

        Args:
            profile: Configuration profile name

        Returns:
            FOClient instance

        Raises:
            ConnectionError: If unable to connect to D365FO
            AuthenticationError: If authentication fails
        """
        async with self._session_lock:
            if profile not in self._client_pool:
                client_config = self._build_client_config(profile)
                if not client_config:
                    raise ValueError(f"Profile '{profile}' configuration is invalid")
                
                client = FOClient(client_config)
                await client.initialize_metadata()

                # Test connection
                try:
                    await self._test_client_connection(client)
                    self._client_pool[profile] = client
                    logger.info(f"Created new D365FO client for profile: {profile}")
                except Exception as e:
                    await client.close()
                    logger.error(f"Failed to create client for profile {profile}: {e}")
                    raise ConnectionError(
                        f"Failed to connect to D365FO: {profile}"
                    ) from e

            return self._client_pool[profile]

    async def test_connection(self, profile: str = "default") -> bool:
        """Test connection for a specific profile.

        Args:
            profile: Configuration profile name

        Returns:
            True if connection is successful
        """
        try:
            client = await self.get_client(profile)
            return await self._test_client_connection(client)
        except Exception as e:
            logger.error(f"Connection test failed for profile {profile}: {e}")
            return False

    async def get_environment_info(self, profile: str = "default") -> dict:
        """Get comprehensive environment information for a profile.

        Args:
            profile: Configuration profile name

        Returns:
            Dictionary with environment information including:
            - base_url: The D365FO environment URL
            - versions: Application, platform, and build version information
            - connectivity: Connection status to the environment
            - metadata_info: Comprehensive metadata and cache information from FOClient
        """
        client = await self.get_client(profile)

        try:
            # Get version information
            app_version = await client.get_application_version()
            platform_version = await client.get_platform_build_version()
            build_version = await client.get_application_build_version()

            # Test connectivity
            connectivity = await self._test_client_connection(client)

            # Get comprehensive metadata and cache information using FOClient's method
            metadata_info = await client.get_metadata_info()

            return {
                "base_url": client.config.base_url,
                "versions": {
                    "application": app_version,
                    "platform": platform_version,
                    "build": build_version,
                },
                "connectivity": connectivity,
                "metadata_info": metadata_info,
            }
        except Exception as e:
            logger.error(f"Failed to get environment info for profile {profile}: {e}")
            raise

    async def cleanup(self, profile: Optional[str] = None):
        """Close client connections.

        Args:
            profile: Specific profile to cleanup, or None for all
        """
        async with self._session_lock:
            if profile and profile in self._client_pool:
                client = self._client_pool.pop(profile)
                await client.close()
                logger.info(f"Closed client for profile: {profile}")
            elif profile is None:
                # Close all clients
                for profile_name, client in self._client_pool.items():
                    try:
                        await client.close()
                        logger.info(f"Closed client for profile: {profile_name}")
                    except Exception as e:
                        logger.error(
                            f"Error closing client for profile {profile_name}: {e}"
                        )
                self._client_pool.clear()

    async def refresh_profile(self, profile: str):
        """Refresh a specific profile by clearing its cached client.
        
        This forces the client manager to recreate the client with
        updated profile configuration on next access.
        
        Args:
            profile: Profile name to refresh
        """
        logger.info(f"Refreshing profile: {profile}")
        # Reload configuration to see any recent changes
        self.profile_manager.reload_config()
        # Clear the cached client for this profile
        await self.cleanup(profile)

    async def refresh_all_profiles(self):
        """Refresh all profiles by clearing the entire client pool.
        
        This forces the client manager to recreate all clients with
        updated profile configurations on next access.
        """
        logger.info("Refreshing all profiles")
        # Reload configuration to see any recent changes
        self.profile_manager.reload_config()
        # Clear all cached clients
        await self.cleanup()

    def _build_client_config(self, profile: str) -> Optional[FOClientConfig]:
        """Build FOClientConfig from profile configuration.

        Args:
            profile: Configuration profile name

        Returns:
            FOClientConfig instance
        """
        # First try to get from profile manager (file-based profiles)
        env_profile = None

        # If requesting "default", resolve to the actual default profile
        if profile == "default" or not profile:
            env_profile = self.profile_manager.get_default_profile()
            if not env_profile:
                # No default profile set, try to get a profile named "default"
                env_profile = self.profile_manager.get_profile("default")
        else:
            # Get specific profile
            env_profile = self.profile_manager.get_profile(profile)

        if env_profile:
            config = self.profile_manager.profile_to_client_config(env_profile)
            # Validate that we have a base_url
            if not config.base_url:
                raise ValueError(
                    f"Profile '{env_profile.name}' has no base_url configured"
                )
            
            # Check if legacy config should override certain settings

            
            return config
        
        raise ValueError(
                    f"Profile '{profile}' not found in profile manager"
                )

    async def shutdown(self):
        """Shutdown the client manager and close all connections."""
        await self.cleanup()
        
    async def _test_client_connection(self, client: FOClient) -> bool:
        """Test a client connection.

        Args:
            client: FOClient instance to test

        Returns:
            True if connection is successful
        """
        try:
            # Try to get application version as a simple connectivity test
            await client.get_application_version()
            return True
        except Exception as e:
            logger.error(f"Client connection test failed: {e}")
            return False

    async def health_check(self) -> dict:
        """Perform health check on all managed clients.

        Returns:
            Dictionary with health check results
        """
        results = {}
        async with self._session_lock:
            for profile, client in self._client_pool.items():
                try:
                    is_healthy = await self._test_client_connection(client)
                    results[profile] = {
                        "healthy": is_healthy,
                        "last_checked": datetime.now(timezone.utc),
                    }
                except Exception as e:
                    results[profile] = {
                        "healthy": False,
                        "error": str(e),
                        "last_checked": datetime.now(timezone.utc),
                    }

        self._last_health_check = datetime.now(timezone.utc)
        return results
