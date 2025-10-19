"""Profile management tools for MCP server."""

import json
import logging
from typing import Any, Dict, List

from mcp import Tool
from mcp.types import TextContent

from ...profile_manager import EnvironmentProfile, ProfileManager
from ..client_manager import D365FOClientManager

logger = logging.getLogger(__name__)


class ProfileTools:
    """Profile management tools for the MCP server."""

    def __init__(self, client_manager: D365FOClientManager):
        """Initialize profile tools.

        Args:
            client_manager: D365FO client manager instance
        """
        self.client_manager = client_manager
        self.profile_manager = ProfileManager()

    def get_tools(self) -> List[Tool]:
        """Get list of profile management tools.

        Returns:
            List of Tool definitions
        """
        return [
            self._get_list_profiles_tool(),
            self._get_get_profile_tool(),
            self._get_create_profile_tool(),
            self._get_update_profile_tool(),
            self._get_delete_profile_tool(),
            self._get_set_default_profile_tool(),
            self._get_get_default_profile_tool(),
            self._get_validate_profile_tool(),
            self._get_test_profile_connection_tool(),
        ]

    def _get_list_profiles_tool(self) -> Tool:
        """Get list profiles tool definition."""
        return Tool(
            name="d365fo_list_profiles",
            description="List all available D365FO environment profiles",
            inputSchema={"type": "object", "properties": {}},
        )

    def _get_get_profile_tool(self) -> Tool:
        """Get profile tool definition."""
        return Tool(
            name="d365fo_get_profile",
            description="Get details of a specific D365FO environment profile",
            inputSchema={
                "type": "object",
                "properties": {
                    "profileName": {
                        "type": "string",
                        "description": "Name of the profile to retrieve",
                    }
                },
                "required": ["profileName"],
            },
        )

    def _get_create_profile_tool(self) -> Tool:
        """Get create profile tool definition."""
        return Tool(
            name="d365fo_create_profile",
            description="Create a new D365FO environment profile",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Profile name"},
                    "baseUrl": {"type": "string", "description": "D365FO base URL"},
                    "authMode": {
                        "type": "string",
                        "description": "Authentication mode",
                        "enum": ["default", "client_credentials"],
                        "default": "default",
                    },
                    "clientId": {
                        "type": "string",
                        "description": "Azure client ID (for client_credentials auth)",
                    },
                    "clientSecret": {
                        "type": "string",
                        "description": "Azure client secret (for client_credentials auth)",
                    },
                    "tenantId": {
                        "type": "string",
                        "description": "Azure tenant ID (for client_credentials auth)",
                    },
                    "credentialSource": {
                        "type": "object",
                        "description": "Credential source configuration",
                        "properties": {
                            "sourceType": {
                                "type": "string",
                                "description": "Type of credential source",
                                "enum": ["environment", "keyvault"]
                            },
                            "clientIdVar": {
                                "type": "string",
                                "description": "Environment variable name for client ID (environment source)",
                                "default": "D365FO_CLIENT_ID"
                            },
                            "clientSecretVar": {
                                "type": "string",
                                "description": "Environment variable name for client secret (environment source)",
                                "default": "D365FO_CLIENT_SECRET"
                            },
                            "tenantIdVar": {
                                "type": "string",
                                "description": "Environment variable name for tenant ID (environment source)",
                                "default": "D365FO_TENANT_ID"
                            },
                            "vaultUrl": {
                                "type": "string",
                                "description": "Azure Key Vault URL (keyvault source)"
                            },
                            "clientIdSecretName": {
                                "type": "string",
                                "description": "Key Vault secret name for client ID (keyvault source)",
                                "default": "D365FO_CLIENT_ID"
                            },
                            "clientSecretSecretName": {
                                "type": "string",
                                "description": "Key Vault secret name for client secret (keyvault source)",
                                "default": "D365FO_CLIENT_SECRET"
                            },
                            "tenantIdSecretName": {
                                "type": "string",
                                "description": "Key Vault secret name for tenant ID (keyvault source)",
                                "default": "D365FO_TENANT_ID"
                            },
                            "keyvaultAuthMode": {
                                "type": "string",
                                "description": "Key Vault authentication mode",
                                "enum": ["default", "client_secret"],
                                "default": "default"
                            },
                            "keyvaultClientId": {
                                "type": "string",
                                "description": "Client ID for Key Vault authentication (client_secret mode)"
                            },
                            "keyvaultClientSecret": {
                                "type": "string",
                                "description": "Client secret for Key Vault authentication (client_secret mode)"
                            },
                            "keyvaultTenantId": {
                                "type": "string",
                                "description": "Tenant ID for Key Vault authentication (client_secret mode)"
                            }
                        },
                        "required": ["sourceType"],
                        "anyOf": [
                            {
                                "properties": {"sourceType": {"const": "environment"}},
                                "additionalProperties": True
                            },
                            {
                                "properties": {"sourceType": {"const": "keyvault"}},
                                "required": ["vaultUrl"],
                                "additionalProperties": True
                            }
                        ]
                    },
                    "verifySsl": {
                        "type": "boolean",
                        "description": "Whether to verify SSL certificates",
                        "default": True,
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Request timeout in seconds",
                        "minimum": 1,
                        "maximum": 300,
                        "default": 60,
                    },
                    "useLabelCache": {
                        "type": "boolean",
                        "description": "Whether to enable label caching",
                        "default": True,
                    },
                    "labelCacheExpiryMinutes": {
                        "type": "integer",
                        "description": "Label cache expiry in minutes",
                        "minimum": 1,
                        "default": 60,
                    },
                    "language": {
                        "type": "string",
                        "description": "Default language code",
                        "default": "en-US",
                    },
                    "cacheDir": {
                        "type": "string",
                        "description": "Cache directory path",
                    },
                    "description": {
                        "type": "string",
                        "description": "Profile description",
                    },
                    "setAsDefault": {
                        "type": "boolean",
                        "description": "Set as default profile",
                        "default": False,
                    },
                },
                "required": ["name", "baseUrl"],
            },
        )

    def _get_update_profile_tool(self) -> Tool:
        """Get update profile tool definition."""
        return Tool(
            name="d365fo_update_profile",
            description="Update an existing D365FO environment profile",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Profile name"},
                    "baseUrl": {"type": "string", "description": "D365FO base URL"},
                    "authMode": {
                        "type": "string",
                        "description": "Authentication mode",
                        "enum": ["default", "client_credentials"],
                    },
                    "clientId": {"type": "string", "description": "Azure client ID"},
                    "clientSecret": {
                        "type": "string",
                        "description": "Azure client secret",
                    },
                    "tenantId": {"type": "string", "description": "Azure tenant ID"},
                    "credentialSource": {
                        "type": "object",
                        "description": "Credential source configuration",
                        "properties": {
                            "sourceType": {
                                "type": "string",
                                "description": "Type of credential source",
                                "enum": ["environment", "keyvault"]
                            },
                            "clientIdVar": {
                                "type": "string",
                                "description": "Environment variable name for client ID (environment source)",
                                "default": "D365FO_CLIENT_ID"
                            },
                            "clientSecretVar": {
                                "type": "string",
                                "description": "Environment variable name for client secret (environment source)",
                                "default": "D365FO_CLIENT_SECRET"
                            },
                            "tenantIdVar": {
                                "type": "string",
                                "description": "Environment variable name for tenant ID (environment source)",
                                "default": "D365FO_TENANT_ID"
                            },
                            "vaultUrl": {
                                "type": "string",
                                "description": "Azure Key Vault URL (keyvault source)"
                            },
                            "clientIdSecretName": {
                                "type": "string",
                                "description": "Key Vault secret name for client ID (keyvault source)",
                                "default": "D365FO_CLIENT_ID"
                            },
                            "clientSecretSecretName": {
                                "type": "string",
                                "description": "Key Vault secret name for client secret (keyvault source)",
                                "default": "D365FO_CLIENT_SECRET"
                            },
                            "tenantIdSecretName": {
                                "type": "string",
                                "description": "Key Vault secret name for tenant ID (keyvault source)",
                                "default": "D365FO_TENANT_ID"
                            },
                            "keyvaultAuthMode": {
                                "type": "string",
                                "description": "Key Vault authentication mode",
                                "enum": ["default", "client_secret"],
                                "default": "default"
                            },
                            "keyvaultClientId": {
                                "type": "string",
                                "description": "Client ID for Key Vault authentication (client_secret mode)"
                            },
                            "keyvaultClientSecret": {
                                "type": "string",
                                "description": "Client secret for Key Vault authentication (client_secret mode)"
                            },
                            "keyvaultTenantId": {
                                "type": "string",
                                "description": "Tenant ID for Key Vault authentication (client_secret mode)"
                            }
                        },
                        "required": ["sourceType"],
                        "anyOf": [
                            {
                                "properties": {"sourceType": {"const": "environment"}},
                                "additionalProperties": True
                            },
                            {
                                "properties": {"sourceType": {"const": "keyvault"}},
                                "required": ["vaultUrl"],
                                "additionalProperties": True
                            }
                        ]
                    },
                    "verifySsl": {
                        "type": "boolean",
                        "description": "Whether to verify SSL certificates",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Request timeout in seconds",
                        "minimum": 1,
                        "maximum": 300,
                    },
                    "useLabelCache": {
                        "type": "boolean",
                        "description": "Whether to enable label caching",
                    },
                    "labelCacheExpiryMinutes": {
                        "type": "integer",
                        "description": "Label cache expiry in minutes",
                        "minimum": 1,
                    },
                    "language": {
                        "type": "string",
                        "description": "Default language code",
                    },
                    "cacheDir": {
                        "type": "string",
                        "description": "Cache directory path",
                    },
                    "description": {
                        "type": "string",
                        "description": "Profile description",
                    },
                },
                "required": ["name"],
            },
        )

    def _get_delete_profile_tool(self) -> Tool:
        """Get delete profile tool definition."""
        return Tool(
            name="d365fo_delete_profile",
            description="Delete a D365FO environment profile",
            inputSchema={
                "type": "object",
                "properties": {
                    "profileName": {
                        "type": "string",
                        "description": "Name of the profile to delete",
                    }
                },
                "required": ["profileName"],
            },
        )

    def _get_set_default_profile_tool(self) -> Tool:
        """Get set default profile tool definition."""
        return Tool(
            name="d365fo_set_default_profile",
            description="Set the default D365FO environment profile",
            inputSchema={
                "type": "object",
                "properties": {
                    "profileName": {
                        "type": "string",
                        "description": "Name of the profile to set as default",
                    }
                },
                "required": ["profileName"],
            },
        )

    def _get_get_default_profile_tool(self) -> Tool:
        """Get default profile tool definition."""
        return Tool(
            name="d365fo_get_default_profile",
            description="Get the current default D365FO environment profile",
            inputSchema={"type": "object", "properties": {}},
        )

    def _get_validate_profile_tool(self) -> Tool:
        """Get validate profile tool definition."""
        return Tool(
            name="d365fo_validate_profile",
            description="Validate a D365FO environment profile configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "profileName": {
                        "type": "string",
                        "description": "Name of the profile to validate",
                    }
                },
                "required": ["profileName"],
            },
        )

    def _get_test_profile_connection_tool(self) -> Tool:
        """Get test profile connection tool definition."""
        return Tool(
            name="d365fo_test_profile_connection",
            description="Test connection for a specific D365FO environment profile",
            inputSchema={
                "type": "object",
                "properties": {
                    "profileName": {
                        "type": "string",
                        "description": "Name of the profile to test",
                    }
                },
                "required": ["profileName"],
            },
        )

    async def execute_list_profiles(self, arguments: dict) -> List[TextContent]:
        """Execute list profiles tool.

        Args:
            arguments: Tool arguments

        Returns:
            List of TextContent responses
        """
        try:
            profiles = self.profile_manager.list_profiles()
            default_profile = self.profile_manager.get_default_profile()

            profile_list = []
            for name, profile in profiles.items():
                profile_info = {
                    "name": profile.name,
                    "baseUrl": profile.base_url,
                    "authMode": profile.auth_mode,
                    "verifySsl": profile.verify_ssl,
                    "language": profile.language,
                    "isDefault": default_profile and default_profile.name == name,
                    "description": profile.description,
                }
                
                # Add credential source type if available
                if profile.credential_source:
                    profile_info["credentialSourceType"] = profile.credential_source.source_type
                
                profile_list.append(profile_info)

            response = {
                "profiles": profile_list,
                "totalCount": len(profile_list),
                "defaultProfile": default_profile.name if default_profile else None,
            }

            return [TextContent(type="text", text=json.dumps(response, indent=2))]

        except Exception as e:
            logger.error(f"List profiles failed: {e}")
            error_response = {"error": str(e), "tool": "d365fo_list_profiles"}
            return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    async def execute_get_profile(self, arguments: dict) -> List[TextContent]:
        """Execute get profile tool.

        Args:
            arguments: Tool arguments

        Returns:
            List of TextContent responses
        """
        try:
            profile_name = arguments["profileName"]
            profile = self.profile_manager.get_profile(profile_name)

            if not profile:
                error_response = {
                    "error": f"Profile not found: {profile_name}",
                    "tool": "d365fo_get_profile",
                }
                return [
                    TextContent(type="text", text=json.dumps(error_response, indent=2))
                ]

            # Convert profile to dict, excluding sensitive data
            profile_dict = {
                "name": profile.name,
                "baseUrl": profile.base_url,
                "authMode": profile.auth_mode,
                "verifySsl": profile.verify_ssl,
                "timeout": profile.timeout,
                "useLabelCache": profile.use_label_cache,
                "labelCacheExpiryMinutes": profile.label_cache_expiry_minutes,
                "language": profile.language,
                "cacheDir": profile.cache_dir,
                "description": profile.description,
            }

            # Add auth details if available (but not secrets)
            if profile.client_id:
                profile_dict["clientId"] = profile.client_id
            if profile.tenant_id:
                profile_dict["tenantId"] = profile.tenant_id

            # Add credential source information if available
            if profile.credential_source:
                cred_source_dict = profile.credential_source.to_dict()
                # Convert to camelCase for JSON response
                credential_source = {
                    "sourceType": cred_source_dict.get("source_type"),
                }
                
                if cred_source_dict.get("source_type") == "environment":
                    credential_source.update({
                        "clientIdVar": cred_source_dict.get("client_id_var"),
                        "clientSecretVar": cred_source_dict.get("client_secret_var"),
                        "tenantIdVar": cred_source_dict.get("tenant_id_var"),
                    })
                elif cred_source_dict.get("source_type") == "keyvault":
                    credential_source.update({
                        "vaultUrl": cred_source_dict.get("vault_url"),
                        "clientIdSecretName": cred_source_dict.get("client_id_secret_name"),
                        "clientSecretSecretName": cred_source_dict.get("client_secret_secret_name"),
                        "tenantIdSecretName": cred_source_dict.get("tenant_id_secret_name"),
                        "keyvaultAuthMode": cred_source_dict.get("keyvault_auth_mode"),
                    })
                    # Only include auth details if using client_secret mode
                    if cred_source_dict.get("keyvault_auth_mode") == "client_secret":
                        credential_source.update({
                            "keyvaultClientId": cred_source_dict.get("keyvault_client_id"),
                            "keyvaultTenantId": cred_source_dict.get("keyvault_tenant_id"),
                        })
                
                profile_dict["credentialSource"] = credential_source

            return [TextContent(type="text", text=json.dumps(profile_dict, indent=2))]

        except Exception as e:
            logger.error(f"Get profile failed: {e}")
            error_response = {
                "error": str(e),
                "tool": "d365fo_get_profile",
                "arguments": arguments,
            }
            return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    async def execute_create_profile(self, arguments: dict) -> List[TextContent]:
        """Execute create profile tool.

        Args:
            arguments: Tool arguments

        Returns:
            List of TextContent responses
        """
        try:
            # Extract parameters
            name = arguments["name"]
            base_url = arguments["baseUrl"]
            auth_mode = arguments.get("authMode", "default")
            client_id = arguments.get("clientId")
            client_secret = arguments.get("clientSecret")
            tenant_id = arguments.get("tenantId")
            verify_ssl = arguments.get("verifySsl", True)
            timeout = arguments.get("timeout", 60)
            use_label_cache = arguments.get("useLabelCache", True)
            label_cache_expiry_minutes = arguments.get("labelCacheExpiryMinutes", 60)
            language = arguments.get("language", "en-US")
            cache_dir = arguments.get("cacheDir")
            description = arguments.get("description")
            set_as_default = arguments.get("setAsDefault", False)

            # Handle credential source
            credential_source = None
            if "credentialSource" in arguments:
                from ...credential_sources import create_credential_source
                cred_source_data = arguments["credentialSource"]
                
                # Convert camelCase to snake_case for the factory function
                source_type = cred_source_data["sourceType"]
                kwargs = {}
                
                if source_type == "environment":
                    if "clientIdVar" in cred_source_data:
                        kwargs["client_id_var"] = cred_source_data["clientIdVar"]
                    if "clientSecretVar" in cred_source_data:
                        kwargs["client_secret_var"] = cred_source_data["clientSecretVar"]
                    if "tenantIdVar" in cred_source_data:
                        kwargs["tenant_id_var"] = cred_source_data["tenantIdVar"]
                elif source_type == "keyvault":
                    kwargs["vault_url"] = cred_source_data["vaultUrl"]
                    if "clientIdSecretName" in cred_source_data:
                        kwargs["client_id_secret_name"] = cred_source_data["clientIdSecretName"]
                    if "clientSecretSecretName" in cred_source_data:
                        kwargs["client_secret_secret_name"] = cred_source_data["clientSecretSecretName"]
                    if "tenantIdSecretName" in cred_source_data:
                        kwargs["tenant_id_secret_name"] = cred_source_data["tenantIdSecretName"]
                    if "keyvaultAuthMode" in cred_source_data:
                        kwargs["keyvault_auth_mode"] = cred_source_data["keyvaultAuthMode"]
                    if "keyvaultClientId" in cred_source_data:
                        kwargs["keyvault_client_id"] = cred_source_data["keyvaultClientId"]
                    if "keyvaultClientSecret" in cred_source_data:
                        kwargs["keyvault_client_secret"] = cred_source_data["keyvaultClientSecret"]
                    if "keyvaultTenantId" in cred_source_data:
                        kwargs["keyvault_tenant_id"] = cred_source_data["keyvaultTenantId"]
                
                credential_source = create_credential_source(source_type, **kwargs)

            # Create profile
            success = self.profile_manager.create_profile(
                name=name,
                base_url=base_url,
                auth_mode=auth_mode,
                client_id=client_id,
                client_secret=client_secret,
                tenant_id=tenant_id,
                verify_ssl=verify_ssl,
                timeout=timeout,
                use_label_cache=use_label_cache,
                label_cache_expiry_minutes=label_cache_expiry_minutes,
                language=language,
                cache_dir=cache_dir,
                description=description,
                credential_source=credential_source,
            )

            if not success:
                error_response = {
                    "error": f"Failed to create profile: {name}",
                    "tool": "d365fo_create_profile",
                }
                return [
                    TextContent(type="text", text=json.dumps(error_response, indent=2))
                ]

            # Set as default if requested
            if set_as_default:
                self.profile_manager.set_default_profile(name)

            # Refresh the client manager to pick up the new profile
            await self.client_manager.refresh_profile(name)
            if set_as_default:
                # If setting as default, also refresh the default profile
                await self.client_manager.refresh_profile("default")

            response = {
                "success": True,
                "profileName": name,
                "message": f"Profile '{name}' created successfully",
                "isDefault": set_as_default,
            }

            return [TextContent(type="text", text=json.dumps(response, indent=2))]

        except Exception as e:
            logger.error(f"Create profile failed: {e}")
            error_response = {
                "error": str(e),
                "tool": "d365fo_create_profile",
                "arguments": arguments,
            }
            return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    async def execute_update_profile(self, arguments: dict) -> List[TextContent]:
        """Execute update profile tool.

        Args:
            arguments: Tool arguments

        Returns:
            List of TextContent responses
        """
        try:
            name = arguments["name"]

            # Remove name from update parameters
            update_params = {k: v for k, v in arguments.items() if k != "name"}

            # Convert parameter names to match profile manager
            param_mapping = {
                "baseUrl": "base_url",
                "authMode": "auth_mode",
                "clientId": "client_id",
                "clientSecret": "client_secret",
                "tenantId": "tenant_id",
                "verifySsl": "verify_ssl",
                "useLabelCache": "use_label_cache",
                "labelCacheExpiryMinutes": "label_cache_expiry_minutes",
                "cacheDir": "cache_dir",
            }

            mapped_params = {}
            for key, value in update_params.items():
                if key == "credentialSource":
                    # Handle credential source
                    from ...credential_sources import create_credential_source
                    cred_source_data = value
                    
                    # Convert camelCase to snake_case for the factory function
                    source_type = cred_source_data["sourceType"]
                    kwargs = {}
                    
                    if source_type == "environment":
                        if "clientIdVar" in cred_source_data:
                            kwargs["client_id_var"] = cred_source_data["clientIdVar"]
                        if "clientSecretVar" in cred_source_data:
                            kwargs["client_secret_var"] = cred_source_data["clientSecretVar"]
                        if "tenantIdVar" in cred_source_data:
                            kwargs["tenant_id_var"] = cred_source_data["tenantIdVar"]
                    elif source_type == "keyvault":
                        kwargs["vault_url"] = cred_source_data["vaultUrl"]
                        if "clientIdSecretName" in cred_source_data:
                            kwargs["client_id_secret_name"] = cred_source_data["clientIdSecretName"]
                        if "clientSecretSecretName" in cred_source_data:
                            kwargs["client_secret_secret_name"] = cred_source_data["clientSecretSecretName"]
                        if "tenantIdSecretName" in cred_source_data:
                            kwargs["tenant_id_secret_name"] = cred_source_data["tenantIdSecretName"]
                        if "keyvaultAuthMode" in cred_source_data:
                            kwargs["keyvault_auth_mode"] = cred_source_data["keyvaultAuthMode"]
                        if "keyvaultClientId" in cred_source_data:
                            kwargs["keyvault_client_id"] = cred_source_data["keyvaultClientId"]
                        if "keyvaultClientSecret" in cred_source_data:
                            kwargs["keyvault_client_secret"] = cred_source_data["keyvaultClientSecret"]
                        if "keyvaultTenantId" in cred_source_data:
                            kwargs["keyvault_tenant_id"] = cred_source_data["keyvaultTenantId"]
                    
                    credential_source = create_credential_source(source_type, **kwargs)
                    mapped_params["credential_source"] = credential_source
                else:
                    mapped_key = param_mapping.get(key, key)
                    mapped_params[mapped_key] = value

            success = self.profile_manager.update_profile(name, **mapped_params)

            if not success:
                error_response = {
                    "error": f"Failed to update profile: {name}",
                    "tool": "d365fo_update_profile",
                }
                return [
                    TextContent(type="text", text=json.dumps(error_response, indent=2))
                ]

            # Refresh the client manager to pick up the updated profile
            await self.client_manager.refresh_profile(name)

            response = {
                "success": True,
                "profileName": name,
                "message": f"Profile '{name}' updated successfully",
                "updatedFields": list(update_params.keys()),
            }

            return [TextContent(type="text", text=json.dumps(response, indent=2))]

        except Exception as e:
            logger.error(f"Update profile failed: {e}")
            error_response = {
                "error": str(e),
                "tool": "d365fo_update_profile",
                "arguments": arguments,
            }
            return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    async def execute_delete_profile(self, arguments: dict) -> List[TextContent]:
        """Execute delete profile tool.

        Args:
            arguments: Tool arguments

        Returns:
            List of TextContent responses
        """
        try:
            profile_name = arguments["profileName"]
            success = self.profile_manager.delete_profile(profile_name)

            if not success:
                error_response = {
                    "error": f"Profile not found or failed to delete: {profile_name}",
                    "tool": "d365fo_delete_profile",
                }
                return [
                    TextContent(type="text", text=json.dumps(error_response, indent=2))
                ]

            # Refresh the client manager to remove the deleted profile
            await self.client_manager.refresh_profile(profile_name)

            response = {
                "success": True,
                "profileName": profile_name,
                "message": f"Profile '{profile_name}' deleted successfully",
            }

            return [TextContent(type="text", text=json.dumps(response, indent=2))]

        except Exception as e:
            logger.error(f"Delete profile failed: {e}")
            error_response = {
                "error": str(e),
                "tool": "d365fo_delete_profile",
                "arguments": arguments,
            }
            return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    async def execute_set_default_profile(self, arguments: dict) -> List[TextContent]:
        """Execute set default profile tool.

        Args:
            arguments: Tool arguments

        Returns:
            List of TextContent responses
        """
        try:
            profile_name = arguments["profileName"]
            success = self.profile_manager.set_default_profile(profile_name)

            if not success:
                error_response = {
                    "error": f"Profile not found: {profile_name}",
                    "tool": "d365fo_set_default_profile",
                }
                return [
                    TextContent(type="text", text=json.dumps(error_response, indent=2))
                ]

            # Refresh the default profile in client manager
            await self.client_manager.refresh_profile("default")

            response = {
                "success": True,
                "profileName": profile_name,
                "message": f"Default profile set to '{profile_name}'",
            }

            return [TextContent(type="text", text=json.dumps(response, indent=2))]

        except Exception as e:
            logger.error(f"Set default profile failed: {e}")
            error_response = {
                "error": str(e),
                "tool": "d365fo_set_default_profile",
                "arguments": arguments,
            }
            return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    async def execute_get_default_profile(self, arguments: dict) -> List[TextContent]:
        """Execute get default profile tool.

        Args:
            arguments: Tool arguments

        Returns:
            List of TextContent responses
        """
        try:
            default_profile = self.profile_manager.get_default_profile()

            if not default_profile:
                response = {"defaultProfile": None, "message": "No default profile set"}
            else:
                response = {
                    "defaultProfile": {
                        "name": default_profile.name,
                        "baseUrl": default_profile.base_url,
                        "authMode": default_profile.auth_mode,
                        "description": default_profile.description,
                    },
                    "message": f"Default profile is '{default_profile.name}'",
                }

            return [TextContent(type="text", text=json.dumps(response, indent=2))]

        except Exception as e:
            logger.error(f"Get default profile failed: {e}")
            error_response = {"error": str(e), "tool": "d365fo_get_default_profile"}
            return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    async def execute_validate_profile(self, arguments: dict) -> List[TextContent]:
        """Execute validate profile tool.

        Args:
            arguments: Tool arguments

        Returns:
            List of TextContent responses
        """
        try:
            profile_name = arguments["profileName"]
            profile = self.profile_manager.get_profile(profile_name)

            if not profile:
                error_response = {
                    "error": f"Profile not found: {profile_name}",
                    "tool": "d365fo_validate_profile",
                }
                return [
                    TextContent(type="text", text=json.dumps(error_response, indent=2))
                ]

            validation_errors = self.profile_manager.validate_profile(profile)

            response = {
                "profileName": profile_name,
                "isValid": len(validation_errors) == 0,
                "errors": validation_errors,
                "message": (
                    "Profile is valid"
                    if not validation_errors
                    else "Profile has validation errors"
                ),
            }

            return [TextContent(type="text", text=json.dumps(response, indent=2))]

        except Exception as e:
            logger.error(f"Validate profile failed: {e}")
            error_response = {
                "error": str(e),
                "tool": "d365fo_validate_profile",
                "arguments": arguments,
            }
            return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    async def execute_test_profile_connection(
        self, arguments: dict
    ) -> List[TextContent]:
        """Execute test profile connection tool.

        Args:
            arguments: Tool arguments

        Returns:
            List of TextContent responses
        """
        try:
            profile_name = arguments["profileName"]
            profile = self.profile_manager.get_profile(profile_name)

            if not profile:
                error_response = {
                    "error": f"Profile not found: {profile_name}",
                    "tool": "d365fo_test_profile_connection",
                }
                return [
                    TextContent(type="text", text=json.dumps(error_response, indent=2))
                ]

            # Test connection using the client manager
            success = await self.client_manager.test_connection(profile_name)

            response = {
                "profileName": profile_name,
                "success": success,
                "baseUrl": profile.base_url,
                "authMode": profile.auth_mode,
                "message": "Connection successful" if success else "Connection failed",
            }

            return [TextContent(type="text", text=json.dumps(response, indent=2))]

        except Exception as e:
            logger.error(f"Test profile connection failed: {e}")
            error_response = {
                "error": str(e),
                "tool": "d365fo_test_profile_connection",
                "arguments": arguments,
            }
            return [TextContent(type="text", text=json.dumps(error_response, indent=2))]
