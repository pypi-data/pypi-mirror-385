"""FastMCP-based D365FO MCP Server implementation.

This module provides a FastMCP-based implementation of the D365FO MCP server
with support for multiple transports (stdio, SSE, streamable-HTTP) and
improved performance, scalability, and deployment flexibility.

Refactored using mixin pattern for modular tool organization.
"""

import asyncio
import json
import logging
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from weakref import WeakValueDictionary

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from .. import __version__
from ..profile_manager import ProfileManager
from .client_manager import D365FOClientManager
from .models import MCPServerConfig
from .mixins import (
    ConnectionToolsMixin,
    CrudToolsMixin,
    DatabaseToolsMixin,
    LabelToolsMixin,
    MetadataToolsMixin,
    PerformanceToolsMixin,
    ProfileToolsMixin,
    SyncToolsMixin,
)

logger = logging.getLogger(__name__)


class SessionContext:
    """Simple session context that can be weakly referenced."""

    def __init__(self, session_id: str, stateless: bool = True):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
        self.stateless = stateless
        self.request_count = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for API compatibility."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "stateless": self.stateless,
            "request_count": self.request_count,
        }

    def __getitem__(self, key):
        """Support dict-like access for backward compatibility."""
        return getattr(self, key, None)

    def __setitem__(self, key, value):
        """Support dict-like access for backward compatibility."""
        setattr(self, key, value)


class FastD365FOMCPServer(
    DatabaseToolsMixin,
    MetadataToolsMixin,
    CrudToolsMixin,
    ProfileToolsMixin,
    SyncToolsMixin,
    LabelToolsMixin,
    ConnectionToolsMixin,
    PerformanceToolsMixin,
):
    """FastMCP-based D365FO MCP Server with multi-transport support."""

    def __init__(self, mcp: FastMCP, config: Optional[Dict[str, Any]] = None,profile_manager: Optional[ProfileManager] = None):
        """Initialize the FastMCP D365FO server.

        Args:
            config: Configuration dictionary with server and transport settings
        """
        if config is not None:
            self.config = config
        else:
            from .fastmcp_utils import load_default_config
            self.config = load_default_config()
        
        self.profile_manager = profile_manager or ProfileManager()
        self.client_manager = D365FOClientManager(self.profile_manager)

 
        self.mcp = mcp

        # Setup dependency injection and features
        self._setup_dependency_injection()
        self._setup_production_features()
        self._setup_mixin_tools()
        self._startup_initialization()

        # Register all components
        self._register_tools()
        self._register_resources()
        self._register_prompts()

    def _setup_dependency_injection(self):
        """Set up dependency injection for tools to access client manager."""
        # Store client manager reference for use in tool functions
        pass

    def _setup_production_features(self):
        """Set up production features including performance monitoring and session management."""
        # Performance monitoring
        self._request_stats = {
            "total_requests": 0,
            "total_errors": 0,
            "avg_response_time": 0.0,
            "last_reset": datetime.now(),
        }
        self._request_times = []
        self._max_request_history = 1000

        # Connection pool monitoring
        self._connection_pool_stats = {
            "active_connections": 0,
            "peak_connections": 0,
            "connection_errors": 0,
            "pool_hits": 0,
            "pool_misses": 0,
        }

        # Stateless session management (for HTTP transport)
        transport_config = self.config.get("server", {}).get("transport", {})
        self._stateless_mode = transport_config.get("http", {}).get("stateless", False)
        self._json_response_mode = transport_config.get("http", {}).get(
            "json_response", False
        )

        if self._stateless_mode:
            logger.info("Stateless HTTP mode enabled - sessions will not be persisted")
            # Use weak references for stateless sessions to allow garbage collection
            self._stateless_sessions = WeakValueDictionary()
        else:
            # Standard session management for stateful mode
            self._active_sessions = {}

        if self._json_response_mode:
            logger.info("JSON response mode enabled - responses will be in JSON format")

        # Performance optimization settings
        perf_config = self.config.get("performance", {})
        self._max_concurrent_requests = perf_config.get("max_concurrent_requests", 10)
        self._request_timeout = perf_config.get("request_timeout", 30)
        self._batch_size = perf_config.get("batch_size", 100)

        # Connection pooling semaphore
        self._request_semaphore = asyncio.Semaphore(self._max_concurrent_requests)

        logger.info(f"Production features configured:")
        logger.info(f"  - Stateless mode: {self._stateless_mode}")
        logger.info(f"  - JSON response mode: {self._json_response_mode}")
        logger.info(f"  - Max concurrent requests: {self._max_concurrent_requests}")
        logger.info(f"  - Request timeout: {self._request_timeout}s")

    def _setup_mixin_tools(self):
        """Setup tool-specific configurations for mixins."""
        self.setup_database_tools()
        # Add other tool setup calls as needed

    def _register_tools(self):
        """Register all tools using mixins."""
        logger.info("Registering tools from mixins...")
        
        # Register tools from each mixin
        self.register_database_tools()
        self.register_metadata_tools()
        self.register_crud_tools()
        self.register_profile_tools()
        self.register_sync_tools()
        self.register_label_tools()
        self.register_connection_tools()
        self.register_performance_tools()
        
        logger.info("All tools registered successfully")

    def _performance_monitor(self, func):
        """Decorator to monitor performance of tool executions."""

        async def wrapper(*args, **kwargs):
            start_time = time.time()

            # Increment request counter
            self._request_stats["total_requests"] += 1

            # Apply request limiting
            async with self._request_semaphore:
                try:
                    # Execute with timeout
                    result = await asyncio.wait_for(
                        func(*args, **kwargs), timeout=self._request_timeout
                    )

                    # Update performance stats
                    execution_time = time.time() - start_time
                    self._request_times.append(execution_time)

                    # Limit request history to prevent memory growth
                    if len(self._request_times) > self._max_request_history:
                        self._request_times = self._request_times[-self._max_request_history:]

                    # Update average response time
                    if self._request_times:
                        self._request_stats["avg_response_time"] = sum(self._request_times) / len(
                            self._request_times
                        )

                    return result

                except asyncio.TimeoutError:
                    self._request_stats["total_errors"] += 1
                    logger.error(f"Request timeout after {self._request_timeout} seconds")
                    raise

                except Exception as e:
                    self._request_stats["total_errors"] += 1
                    logger.error(f"Request execution failed: {e}")
                    raise

        return wrapper

    def get_performance_stats(self) -> dict:
        """Get current performance statistics.
        
        Returns:
            Dictionary containing performance metrics
        """
        current_time = time.time()
        
        # Calculate percentiles for response times
        percentiles = {}
        if self._request_times:
            sorted_times = sorted(self._request_times)
            percentiles = {
                "p50": self._percentile(sorted_times, 50),
                "p90": self._percentile(sorted_times, 90),
                "p95": self._percentile(sorted_times, 95),
                "p99": self._percentile(sorted_times, 99),
            }
        
        return {
            "request_stats": self._request_stats.copy(),
            "connection_pool_stats": self._connection_pool_stats.copy(),
            "response_time_percentiles": percentiles,
            "active_sessions": len(getattr(self, '_active_sessions', {})),
            "stateless_sessions": len(getattr(self, '_stateless_sessions', {})),
            "server_uptime_seconds": current_time - getattr(self, '_server_start_time', current_time),
            "memory_usage": {
                "request_history_count": len(self._request_times),
                "max_request_history": self._max_request_history,
            },
        }

    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate the specified percentile of a dataset.
        
        Args:
            data: Sorted list of numeric values
            percentile: Percentile to calculate (0-100)
            
        Returns:
            Percentile value
        """
        if not data:
            return 0.0
        
        k = (len(data) - 1) * percentile / 100
        f = int(k)
        c = k - f
        
        if f + 1 < len(data):
            return data[f] + (c * (data[f + 1] - data[f]))
        else:
            return data[f]

    def _cleanup_expired_sessions(self):
        """Clean up expired sessions for memory management."""
        if hasattr(self, '_active_sessions'):
            current_time = datetime.now()
            expired_sessions = []
            
            for session_id, session in self._active_sessions.items():
                # Sessions expire after 1 hour of inactivity
                if (current_time - session.last_accessed).total_seconds() > 3600:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self._active_sessions[session_id]
                logger.debug(f"Cleaned up expired session: {session_id}")
            
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

    def _get_session_context(self, session_id: Optional[str] = None) -> SessionContext:
        """Get or create session context for request tracking."""
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
        
        if self._stateless_mode:
            # For stateless mode, create temporary session
            return SessionContext(session_id, stateless=True)
        else:
            # For stateful mode, track sessions
            if session_id not in self._active_sessions:
                self._active_sessions[session_id] = SessionContext(session_id, stateless=False)
            return self._active_sessions[session_id]

    def _record_request_time(self, execution_time: float):
        """Record request execution time for performance monitoring."""
        self._request_times.append(execution_time)
        
        # Limit request history to prevent memory growth
        if len(self._request_times) > self._max_request_history:
            self._request_times = self._request_times[-self._max_request_history:]
        
        # Update average response time
        if self._request_times:
            self._request_stats["avg_response_time"] = sum(self._request_times) / len(
                self._request_times
            )

    def _startup_initialization(self):
        """Perform startup initialization tasks."""
        # Set server start time for uptime calculation
        self._server_start_time = time.time()
        
        # Initialize any additional startup tasks
        logger.info("FastMCP server startup initialization completed")

    async def cleanup(self):
        """Clean up server resources."""
        # Clean up expired sessions
        self._cleanup_expired_sessions()
        
        # Reset performance stats if needed
        logger.debug("Server cleanup completed")

    def _register_resources(self):
        """Register D365FO resources using FastMCP decorators."""

        @self.mcp.resource("d365fo://entities/{entity_name}")
        async def entity_resource(entity_name: str) -> str:
            """Get entity metadata and sample data.
            
            Args:
                entity_name: Name of the entity to retrieve
                
            Returns:
                JSON string with entity information
            """
            try:
                client = await self.client_manager.get_client("default")
                
                # Get entity schema
                entity_info = await client.get_public_entity_info(entity_name)
                if not entity_info:
                    return json.dumps({"error": f"Entity '{entity_name}' not found"})
                
                # Get sample data if entity has data service enabled
                sample_data = []
                try:
                    from ..models import QueryOptions
                    options = QueryOptions(top=5)  # Get 5 sample records
                    result = await client.get_entities(entity_name, options=options)
                    sample_data = result.get("value", [])
                except Exception:
                    pass  # Ignore errors getting sample data
                
                return json.dumps({
                    "entity_name": entity_name,
                    "schema": entity_info.to_dict(),
                    "sample_data": sample_data,
                    "sample_count": len(sample_data),
                })
                
            except Exception as e:
                logger.error(f"Entity resource failed: {e}")
                return json.dumps({"error": str(e), "entity_name": entity_name})

        @self.mcp.resource("d365fo://metadata/environment")
        async def environment_metadata() -> str:
            """Get D365FO environment metadata.
            
            Returns:
                JSON string with environment information
            """
            try:
                # Get environment info from default profile
                result = await self.client_manager.get_environment_info("default")
                return json.dumps(result, indent=2)
                
            except Exception as e:
                logger.error(f"Environment metadata resource failed: {e}")
                return json.dumps({"error": str(e)})

        @self.mcp.resource("d365fo://profiles")
        async def profiles_resource() -> str:
            """Get all available profiles.
            
            Returns:
                JSON string with profiles list
            """
            try:
                profiles = self.profile_manager.list_profiles()
                # Convert Profile objects to dictionaries for JSON serialization
                profiles_data = []
                for profile in profiles:
                    if hasattr(profile, 'to_dict'):
                        profiles_data.append(profile.to_dict())
                    else:
                        # Fallback: convert to dict manually
                        profiles_data.append({
                            "name": getattr(profile, 'name', 'Unknown'),
                            "base_url": getattr(profile, 'base_url', ''),
                            "client_id": getattr(profile, 'client_id', ''),
                            "tenant_id": getattr(profile, 'tenant_id', ''),
                            # Add other relevant fields as needed
                        })
                
                return json.dumps({
                    "profiles": profiles_data,
                    "total_count": len(profiles_data),
                })
                
            except Exception as e:
                logger.error(f"Profiles resource failed: {e}")
                return json.dumps({"error": str(e)})

        @self.mcp.resource("d365fo://query/{entity_name}")
        async def query_resource(entity_name: str) -> str:
            """Execute a simple query on an entity.
            
            Args:
                entity_name: Name of the entity to query
                
            Returns:
                JSON string with query results
            """
            try:
                client = await self.client_manager.get_client("default")
                
                from ..models import QueryOptions
                options = QueryOptions(top=10)  # Get 10 records
                result = await client.get_entities(entity_name, options=options)
                
                return json.dumps({
                    "entity_name": entity_name,
                    "data": result.get("value", []),
                    "count": len(result.get("value", [])),
                    "has_more": "@odata.nextLink" in result,
                })
                
            except Exception as e:
                logger.error(f"Query resource failed: {e}")
                return json.dumps({"error": str(e), "entity_name": entity_name})

        logger.info("Registered D365FO resources")

    def _register_prompts(self):
        """Register D365FO prompts using FastMCP decorators."""

        @self.mcp.prompt()
        async def d365fo_entity_analysis(entity_name: str) -> str:
            """Analyze a D365FO data entity structure and provide insights.
            
            Args:
                entity_name: Name of the entity to analyze
                
            Returns:
                Analysis prompt text
            """
            try:
                client = await self.client_manager.get_client("default")
                
                # Get entity information
                entity_info = await client.get_public_entity_info(entity_name)
                if not entity_info:
                    return f"Entity '{entity_name}' not found in D365 F&O."
                
                # Build analysis
                analysis = [
                    f"# D365 F&O Entity Analysis: {entity_name}",
                    f"",
                    f"**Entity Name**: {entity_info.name}",
                    f"**Label**: {entity_info.label_text or 'N/A'}",
                    f"**Category**: {getattr(entity_info, 'entity_category', 'Unknown')}",
                    f"**OData Enabled**: {'Yes' if getattr(entity_info, 'data_service_enabled', False) else 'No'}",
                    f"**DMF Enabled**: {'Yes' if getattr(entity_info, 'data_management_enabled', False) else 'No'}",
                    f"**Read Only**: {'Yes' if getattr(entity_info, 'is_read_only', False) else 'No'}",
                    f"",
                ]
                
                # Add properties information
                if hasattr(entity_info, 'properties') and entity_info.properties:
                    analysis.extend([
                        f"## Properties ({len(entity_info.properties)} total)",
                        f"",
                    ])
                    
                    # Key fields
                    key_props = [p for p in entity_info.properties if getattr(p, 'is_key', False)]
                    if key_props:
                        analysis.append("**Key Fields:**")
                        for prop in key_props:
                            analysis.append(f"- {prop.name} ({prop.data_type})")
                        analysis.append("")
                    
                    # Required fields
                    required_props = [p for p in entity_info.properties if getattr(p, 'is_mandatory', False)]
                    if required_props:
                        analysis.append("**Required Fields:**")
                        for prop in required_props:
                            analysis.append(f"- {prop.name} ({prop.data_type})")
                        analysis.append("")
                
                # Add actions information
                if hasattr(entity_info, 'actions') and entity_info.actions:
                    analysis.extend([
                        f"## Available Actions ({len(entity_info.actions)} total)",
                        f"",
                    ])
                    
                    for action in entity_info.actions:
                        analysis.append(f"- **{action.name}**: {action.binding_kind}")
                
                return "\n".join(analysis)
                
            except Exception as e:
                return f"Error analyzing entity '{entity_name}': {str(e)}"

        @self.mcp.prompt()
        async def d365fo_environment_summary() -> str:
            """Generate a summary of the D365FO environment.
            
            Returns:
                Environment summary prompt text
            """
            try:
                # Get environment info
                env_info = await self.client_manager.get_environment_info("default")
                
                summary = [
                    "# D365 Finance & Operations Environment Summary",
                    "",
                    f"**Environment**: {env_info.get('environment_name', 'Unknown')}",
                    f"**Base URL**: {env_info.get('base_url', 'N/A')}",
                    f"**Application Version**: {env_info.get('versions', {}).get('application', env_info.get('version', {}).get('application_version', 'Unknown'))}",
                    f"**Platform Version**: {env_info.get('versions', {}).get('platform', env_info.get('platform_version', 'Unknown'))}",
                    f"**Build Version**: {env_info.get('versions', {}).get('build', 'Unknown')}",
                    "",
                    "## Available Features",
                    "- OData API for data access",
                    "- Data Management Framework (DMF)",
                    "- Action methods for business operations",
                    "- Label system for multilingual support",
                    "",
                    "## Connection Status",
                    f"**Status**: {'Connected' if env_info.get('connection_status') == 'success' else 'Error'}",
                    f"**Authentication**: {env_info.get('auth_mode', 'Unknown')}",
                    "",
                ]
                
                return "\n".join(summary)
                
            except Exception as e:
                return f"Error getting environment summary: {str(e)}"

        logger.info("Registered D365FO prompts")


    # Server lifecycle methods (preserved from original)
    async def shutdown(self):
        """Gracefully shutdown the server."""
        logger.info("Shutting down FastD365FOMCPServer...")
        
        # Clean up sessions
        self._cleanup_expired_sessions()
        
        # Shutdown client manager
        if hasattr(self.client_manager, 'shutdown'):
            await self.client_manager.shutdown() # type: ignore
            
        logger.info("FastD365FOMCPServer shutdown completed")