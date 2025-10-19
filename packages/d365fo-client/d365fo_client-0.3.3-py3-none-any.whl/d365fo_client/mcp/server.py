"""Main MCP Server implementation for d365fo-client."""

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

from mcp import GetPromptResult, Resource, Tool
from mcp.server import InitializationOptions, Server

from d365fo_client.credential_sources import CredentialSource, EnvironmentCredentialSource

from .. import __version__
from ..profile_manager import ProfileManager
from mcp.server.lowlevel.server import NotificationOptions
from mcp.types import Prompt, PromptArgument, PromptMessage, TextContent

from .client_manager import D365FOClientManager
from .models import MCPServerConfig
from .prompts import AVAILABLE_PROMPTS
from .resources import (
    DatabaseResourceHandler,
    EntityResourceHandler,
    EnvironmentResourceHandler,
    MetadataResourceHandler,
    QueryResourceHandler,
)
from .tools import ConnectionTools, CrudTools, DatabaseTools, JsonServiceTools, LabelTools, MetadataTools, ProfileTools, SyncTools

logger = logging.getLogger(__name__)


class D365FOMCPServer:
    """MCP Server for Microsoft Dynamics 365 Finance & Operations."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the MCP server.

        Args:
            config: Configuration dictionary
        """
        self.config = config or self._load_default_config()
        self.server = Server("d365fo-mcp-server")
        self.profile_manager = ProfileManager()
        self.client_manager = D365FOClientManager(self.config, self.profile_manager)

        # Initialize resource handlers
        self.entity_handler = EntityResourceHandler(self.client_manager)
        self.environment_handler = EnvironmentResourceHandler(self.client_manager)
        self.metadata_handler = MetadataResourceHandler(self.client_manager)
        self.query_handler = QueryResourceHandler(self.client_manager)
        self.database_handler = DatabaseResourceHandler(self.client_manager)

        # Initialize tool handlers
        self.connection_tools = ConnectionTools(self.client_manager)
        self.crud_tools = CrudTools(self.client_manager)
        self.metadata_tools = MetadataTools(self.client_manager)
        self.label_tools = LabelTools(self.client_manager)
        self.profile_tools = ProfileTools(self.client_manager)
        self.database_tools = DatabaseTools(self.client_manager)
        self.sync_tools = SyncTools(self.client_manager)
        self.json_service_tools = JsonServiceTools(self.client_manager)

        # Tool registry for execution
        self.tool_registry = {}

        self._setup_handlers()

    def _setup_handlers(self):
        """Set up MCP server handlers."""

        # Resource handlers
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """Handle list resources request."""
            try:
                resources = []

                # Add entity resources
                entity_resources = await self.entity_handler.list_resources()
                resources.extend(entity_resources)

                # Add environment resources
                env_resources = await self.environment_handler.list_resources()
                resources.extend(env_resources)

                # Add metadata resources
                metadata_resources = await self.metadata_handler.list_resources()
                resources.extend(metadata_resources)

                # Add query resources
                query_resources = await self.query_handler.list_resources()
                resources.extend(query_resources)

                # Add database resources
                database_resources = await self.database_handler.list_resources()
                resources.extend(database_resources)

                logger.info(f"Listed {len(resources)} total resources")
                return resources
            except Exception as e:
                logger.error(f"Error listing resources: {e}")
                return []

        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Handle read resource request."""
            try:
                if uri.startswith("d365fo://entities/"):
                    return await self.entity_handler.read_resource(uri)
                elif uri.startswith("d365fo://environment/"):
                    return await self.environment_handler.read_resource(uri)
                elif uri.startswith("d365fo://metadata/"):
                    return await self.metadata_handler.read_resource(uri)
                elif uri.startswith("d365fo://queries/"):
                    return await self.query_handler.read_resource(uri)
                elif uri.startswith("d365fo://database/"):
                    return await self.database_handler.read_resource(uri)
                else:
                    raise ValueError(f"Unknown resource URI: {uri}")
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                raise

        # Prompt handlers
        @self.server.list_prompts()
        async def handle_list_prompts() -> List[Prompt]:
            """Handle list prompts request."""
            try:
                logger.info("Handling list_prompts request")
                prompts = []

                for prompt_name, prompt_config in AVAILABLE_PROMPTS.items():
                    logger.info(f"Processing prompt: {prompt_name}")
                    # Convert our prompt config to MCP Prompt format
                    prompt_args = []
                    if hasattr(prompt_config.get("arguments"), "__annotations__"):
                        # Extract arguments from dataclass annotations
                        annotations = prompt_config["arguments"].__annotations__
                        for arg_name, arg_type in annotations.items():
                            prompt_args.append(
                                PromptArgument(
                                    name=arg_name,
                                    description=f"Parameter: {arg_name}",
                                    required=False,  # Make all optional for now
                                )
                            )

                    prompt = Prompt(
                        name=prompt_name,
                        description=prompt_config["description"],
                        arguments=prompt_args,
                    )
                    prompts.append(prompt)

                logger.info(f"Listed {len(prompts)} prompts")
                return prompts
            except Exception as e:
                logger.error(f"Error listing prompts: {e}")
                return []

        @self.server.get_prompt()
        async def handle_get_prompt(
            name: str, arguments: Optional[Dict[str, Any]] = None
        ) -> GetPromptResult:
            """Handle get prompt request."""
            try:
                logger.info(f"Handling get_prompt request for: {name}")
                if name not in AVAILABLE_PROMPTS:
                    raise ValueError(f"Unknown prompt: {name}")

                prompt_config = AVAILABLE_PROMPTS[name]
                template = prompt_config["template"]

                # For now, return the template as-is
                # In the future, we could process arguments and customize the template
                messages = [
                    PromptMessage(
                        role="user", content=TextContent(type="text", text=template)
                    )
                ]

                logger.info(f"Returning prompt template for: {name}")
                return GetPromptResult(
                    description=prompt_config["description"], messages=messages
                )
            except Exception as e:
                logger.error(f"Error getting prompt {name}: {e}")
                raise

        # Tool handlers
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """Handle list tools request."""
            try:
                tools = []

                # Add connection tools
                connection_tools = self.connection_tools.get_tools()
                tools.extend(connection_tools)

                # Add CRUD tools
                crud_tools = self.crud_tools.get_tools()
                tools.extend(crud_tools)

                # Add metadata tools
                metadata_tools = self.metadata_tools.get_tools()
                tools.extend(metadata_tools)

                # Add label tools
                label_tools = self.label_tools.get_tools()
                tools.extend(label_tools)

                # Add profile tools
                profile_tools = self.profile_tools.get_tools()
                tools.extend(profile_tools)

                # Add database tools
                database_tools = self.database_tools.get_tools()
                tools.extend(database_tools)

                # Add sync tools
                sync_tools = self.sync_tools.get_tools()
                tools.extend(sync_tools)

                # Add JSON service tools
                json_service_tools = self.json_service_tools.get_tools()
                tools.extend(json_service_tools)

                # Register tools for execution
                for tool in tools:
                    self.tool_registry[tool.name] = tool

                logger.info(f"Listed {len(tools)} tools")
                return tools
            except Exception as e:
                logger.error(f"Error listing tools: {e}")
                return []

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> List[TextContent]:
            """Handle tool execution request."""
            try:
                logger.info(f"Executing tool: {name} with arguments: {arguments}")

                # Route to appropriate tool handler
                if name == "d365fo_test_connection":
                    return await self.connection_tools.execute_test_connection(
                        arguments
                    )
                elif name == "d365fo_get_environment_info":
                    return await self.connection_tools.execute_get_environment_info(
                        arguments
                    )
                elif name == "d365fo_query_entities":
                    return await self.crud_tools.execute_query_entities(arguments)
                elif name == "d365fo_get_entity_record":
                    return await self.crud_tools.execute_get_entity_record(arguments)
                elif name == "d365fo_create_entity_record":
                    return await self.crud_tools.execute_create_entity_record(arguments)
                elif name == "d365fo_update_entity_record":
                    return await self.crud_tools.execute_update_entity_record(arguments)
                elif name == "d365fo_delete_entity_record":
                    return await self.crud_tools.execute_delete_entity_record(arguments)
                elif name == "d365fo_call_action":
                    return await self.crud_tools.execute_call_action(arguments)
                elif name == "d365fo_search_entities":
                    return await self.metadata_tools.execute_search_entities(arguments)
                elif name == "d365fo_get_entity_schema":
                    return await self.metadata_tools.execute_get_entity_schema(
                        arguments
                    )
                elif name == "d365fo_search_actions":
                    return await self.metadata_tools.execute_search_actions(arguments)
                elif name == "d365fo_search_enumerations":
                    return await self.metadata_tools.execute_search_enumerations(
                        arguments
                    )
                elif name == "d365fo_get_enumeration_fields":
                    return await self.metadata_tools.execute_get_enumeration_fields(
                        arguments
                    )
                elif name == "d365fo_get_installed_modules":
                    return await self.metadata_tools.execute_get_installed_modules(
                        arguments
                    )
                elif name == "d365fo_get_label":
                    return await self.label_tools.execute_get_label(arguments)
                elif name == "d365fo_get_labels_batch":
                    return await self.label_tools.execute_get_labels_batch(arguments)
                elif name == "d365fo_list_profiles":
                    return await self.profile_tools.execute_list_profiles(arguments)
                elif name == "d365fo_get_profile":
                    return await self.profile_tools.execute_get_profile(arguments)
                elif name == "d365fo_create_profile":
                    return await self.profile_tools.execute_create_profile(arguments)
                elif name == "d365fo_update_profile":
                    return await self.profile_tools.execute_update_profile(arguments)
                elif name == "d365fo_delete_profile":
                    return await self.profile_tools.execute_delete_profile(arguments)
                elif name == "d365fo_set_default_profile":
                    return await self.profile_tools.execute_set_default_profile(
                        arguments
                    )
                elif name == "d365fo_get_default_profile":
                    return await self.profile_tools.execute_get_default_profile(
                        arguments
                    )
                elif name == "d365fo_validate_profile":
                    return await self.profile_tools.execute_validate_profile(arguments)
                elif name == "d365fo_test_profile_connection":
                    return await self.profile_tools.execute_test_profile_connection(
                        arguments
                    )
                elif name == "d365fo_execute_sql_query":
                    return await self.database_tools.execute_sql_query(arguments)
                elif name == "d365fo_get_database_schema":
                    return await self.database_tools.execute_get_database_schema(arguments)
                elif name == "d365fo_get_table_info":
                    return await self.database_tools.execute_get_table_info(arguments)
                elif name == "d365fo_get_database_statistics":
                    return await self.database_tools.execute_get_database_statistics(arguments)
                elif name == "d365fo_start_sync":
                    return await self.sync_tools.execute_start_sync(arguments)
                elif name == "d365fo_get_sync_progress":
                    return await self.sync_tools.execute_get_sync_progress(arguments)
                elif name == "d365fo_cancel_sync":
                    return await self.sync_tools.execute_cancel_sync(arguments)
                elif name == "d365fo_list_sync_sessions":
                    return await self.sync_tools.execute_list_sync_sessions(arguments)
                elif name == "d365fo_get_sync_history":
                    return await self.sync_tools.execute_get_sync_history(arguments)
                elif name == "d365fo_call_json_service":
                    return await self.json_service_tools.execute_call_json_service(arguments)
                elif name == "d365fo_call_sql_diagnostic_service":
                    return await self.json_service_tools.execute_call_sql_diagnostic_service(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")

            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                error_response = {"error": str(e), "tool": name, "arguments": arguments}
                return [TextContent(type="text", text=str(error_response))]

    async def run(self, transport_type: str = "stdio"):
        """Run the MCP server.

        Args:
            transport_type: Transport type (stdio, sse, etc.)
        """
        try:
            logger.info(f"Starting D365FO MCP Server v{__version__}...")

            # Perform conditional startup initialization
            await self._startup_initialization()

            if transport_type == "stdio":
                from mcp.server.stdio import stdio_server

                async with stdio_server() as (read_stream, write_stream):
                    await self.server.run(
                        read_stream,
                        write_stream,
                        InitializationOptions(
                            server_name="d365fo-mcp-server",
                            server_version=__version__,
                            capabilities=self.server.get_capabilities(
                                notification_options=NotificationOptions(),
                                experimental_capabilities={},
                            ),
                        ),
                    )
            else:
                raise ValueError(f"Unsupported transport type: {transport_type}")

        except Exception as e:
            logger.error(f"Error running MCP server: {e}")
            raise
        finally:
            await self.cleanup()

    async def _startup_initialization(self):
        """Perform startup initialization based on configuration."""
        try:
            startup_mode = self.config.get("startup_mode", "profile_only")
            
            if startup_mode == "profile_only":
                logger.info("Server started in profile-only mode")
                logger.info("No environment variables configured - use profile management tools to configure D365FO connections")
                
            elif startup_mode == "default_auth":
                logger.info("Server started with default authentication mode")
                logger.info("D365FO_BASE_URL configured - performing health checks and creating default profile with default auth")
                
                # Perform health checks and create default profile
                await self._startup_health_checks()
                await self._create_default_profile_if_needed()
                
            elif startup_mode == "client_credentials":
                logger.info("Server started with client credentials authentication mode")
                logger.info("Full D365FO environment variables configured - performing health checks and creating default profile with client credentials")
                
                # Perform health checks and create default profile
                await self._startup_health_checks()
                await self._create_default_profile_if_needed()
                
            else:
                logger.warning(f"Unknown startup mode: {startup_mode}")

        except Exception as e:
            logger.error(f"Startup initialization failed: {e}")
            # Don't fail startup on initialization failures - allow server to start in profile-only mode

    async def _create_default_profile_if_needed(self):
        """Create a default profile from environment variables if needed."""
        try:
            # Check if default profile already exists
            existing_default = self.profile_manager.get_default_profile()
            if existing_default:
                logger.info(f"Default profile already exists: {existing_default.name}")
                return

            # Get environment variables with correct names
            base_url = os.getenv("D365FO_BASE_URL")
            client_id = os.getenv("D365FO_CLIENT_ID")
            client_secret = os.getenv("D365FO_CLIENT_SECRET")
            tenant_id = os.getenv("D365FO_TENANT_ID")

            if not base_url:
                logger.warning("Cannot create default profile - D365FO_BASE_URL not set")
                return

            # Determine authentication mode based on startup mode
            startup_mode = self.config.get("startup_mode", "profile_only")
            
            if startup_mode == "client_credentials":
                auth_mode = "client_credentials"
                if not all([client_id, client_secret, tenant_id]):
                    logger.error("Client credentials mode requires D365FO_CLIENT_ID, D365FO_CLIENT_SECRET, and D365FO_TENANT_ID")
                    return
            else:
                auth_mode = "default"
                # Clear client credentials for default auth mode
                client_id = None
                client_secret = None
                tenant_id = None

            # Create default profile with unique name
            profile_name = "default-from-env"
            
            # Check if profile with this name already exists
            existing_profile = self.profile_manager.get_profile(profile_name)
            if existing_profile:
                logger.info(f"Profile '{profile_name}' already exists, setting as default")
                self.profile_manager.set_default_profile(profile_name)
                return

            credential_source = None
            if startup_mode == "client_credentials":
                credential_source = EnvironmentCredentialSource()

            success = self.profile_manager.create_profile(
                name=profile_name,
                base_url=base_url,
                auth_mode=auth_mode,
                client_id=None, #use from env var
                client_secret=None, #use from env var
                tenant_id=None, #use from env var
                description=f"Auto-created from environment variables at startup (mode: {startup_mode})",
                use_label_cache=True,
                timeout=60,
                verify_ssl=True,
                credential_source=credential_source
            )

            if success:
                # Set as default profile
                self.profile_manager.set_default_profile(profile_name)
                logger.info(f"Created and set default profile: {profile_name}")
                logger.info(f"Profile configured for: {base_url}")
                logger.info(f"Authentication mode: {auth_mode}")
                
                if auth_mode == "client_credentials":
                    logger.info(f"Client ID: {client_id}")
                    logger.info(f"Tenant ID: {tenant_id}")
                    
            else:
                logger.warning(f"Failed to create default profile: {profile_name}")

        except Exception as e:
            logger.error(f"Error creating default profile: {e}")

    async def _startup_health_checks(self):
        """Perform startup health checks."""
        try:
            logger.info("Performing startup health checks...")

            # Test default connection
            connection_ok = await self.client_manager.test_connection()
            if not connection_ok:
                logger.warning("Default connection test failed during startup")
            else:
                logger.info("Default connection test passed")

            # Get environment info to verify functionality
            try:
                env_info = await self.client_manager.get_environment_info()
                logger.info(f"Connected to D365FO environment: {env_info['base_url']}")
                logger.info(
                    f"Application version: {env_info['versions']['application']}"
                )
            except Exception as e:
                logger.warning(f"Could not retrieve environment info: {e}")

        except Exception as e:
            logger.error(f"Startup health checks failed: {e}")
            # Don't fail startup on health check failures

    async def cleanup(self):
        """Clean up resources."""
        try:
            logger.info("Cleaning up D365FO MCP Server...")
            await self.client_manager.cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration.

        Returns:
            Default configuration dictionary
        """
        return {
            "default_environment": {
                "base_url": os.getenv(
                    "D365FO_BASE_URL",
                    "https://usnconeboxax1aos.cloud.onebox.dynamics.com",
                ),
                "use_default_credentials": True,
                "use_cache_first": True,
                "timeout": 60,
                "verify_ssl": True,
                "use_label_cache": True,
            },
            "cache": {
                "metadata_cache_dir": os.path.expanduser("~/.d365fo-mcp/cache"),
                "label_cache_expiry_minutes": 120,
                "use_label_cache": True,
                "cache_size_limit_mb": 100,
            },
            "performance": {
                "max_concurrent_requests": 10,
                "connection_pool_size": 5,
                "request_timeout": 30,
                "batch_size": 100,
            },
            "security": {
                "encrypt_cached_tokens": True,
                "token_expiry_buffer_minutes": 5,
                "max_retry_attempts": 3,
            },
            "profiles": {
                "default": {
                    "base_url": os.getenv(
                        "D365FO_BASE_URL",
                        "https://usnconeboxax1aos.cloud.onebox.dynamics.com",
                    ),
                    "use_default_credentials": True,
                }
            },
        }
