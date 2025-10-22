"""
Scientific Model Context Protocol (SMCP) - Enhanced MCP Server with ToolUniverse Integration

SMCP is a sophisticated MCP (Model Context Protocol) server that bridges the gap between
AI agents and scientific tools. It seamlessly integrates ToolUniverse's extensive
collection of 350+ scientific tools with the MCP protocol, enabling AI systems to
access scientific databases, perform complex analyses, and execute scientific workflows.

The SMCP module provides a complete solution for exposing scientific computational
resources through the standardized MCP protocol, making it easy for AI agents to
discover, understand, and execute scientific tools in a unified manner.

Usage Patterns
--------------

Quick Start:

```python
# High-performance server with custom configuration
server = SMCP(
    name="Production Scientific API",
    tool_categories=["uniprot", "ChEMBL", "opentarget", "hpa"],
    max_workers=20,
    search_enabled=True
)
server.run_simple(
    transport="http",
    host="0.0.0.0",
    port=7000
)
```

Client Integration:
```python
# Using MCP client to discover and use tools
import json

# Discover protein analysis tools
response = await client.call_tool("find_tools", {
    "query": "protein structure analysis",
    "limit": 5
})

# Use discovered tool
result = await client.call_tool("UniProt_get_entry_by_accession", {
    "arguments": json.dumps({"accession": "P05067"})
})
```

Architecture
------------

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │◄──►│      SMCP        │◄──►│  ToolUniverse   │
│  (AI Agent)     │    │     Server       │    │   (350+ Tools)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Scientific      │
                       │  Databases &     │
                       │  Services        │
                       └──────────────────┘

The SMCP server acts as an intelligent middleware layer that:
1. Receives MCP requests from AI agents/clients
2. Translates requests to ToolUniverse tool calls
3. Executes tools against scientific databases/services
4. Returns formatted results via MCP protocol
5. Provides intelligent tool discovery and recommendation

Integration Points
------------------

MCP Protocol Layer:
    - Standard MCP methods (tools/list, tools/call, etc.)
    - Custom scientific methods (tools/find, tools/search)
    - Transport-agnostic communication (stdio, HTTP, SSE)
    - Proper error codes and JSON-RPC 2.0 compliance

ToolUniverse Integration:
    - Dynamic tool loading and configuration
    - Schema transformation and validation
    - Execution wrapper with error handling
    - Category-based tool organization

AI Agent Interface:
    - Natural language tool discovery
    - Contextual tool recommendations
    - Structured parameter schemas
    - Comprehensive tool documentation
"""

import asyncio
import functools
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Union, Callable, Literal

try:
    from fastmcp import FastMCP

    FASTMCP_AVAILABLE = True
except ImportError:
    # Use a simple print here since logging isn't available yet
    print(
        "FastMCP is not available. SMCP is built on top of FastMCP, which is a required dependency."
    )

from .execute_function import ToolUniverse
from .logging_config import (
    get_logger,
)


class SMCP(FastMCP):
    """
    Scientific Model Context Protocol (SMCP) Server

    SMCP is an enhanced MCP (Model Context Protocol) server that seamlessly integrates
    ToolUniverse's extensive collection of scientific and scientific tools with the
    FastMCP framework. It provides a unified, AI-accessible interface for scientific
    computing, data analysis, and research workflows.

    The SMCP server extends standard MCP capabilities with scientific domain expertise,
    intelligent tool discovery, and optimized configurations for research applications.
    It automatically handles the complex task of exposing hundreds of specialized tools
    through a consistent, well-documented interface.

    Key Features:
    ============
    🔬 **Scientific Tool Integration**: Native access to 350+ specialized tools covering
       scientific databases, literature search, clinical data, genomics, proteomics,
       chemical informatics, and AI-powered analysis capabilities.

    🧠 **AI-Powered Tool Discovery**: Multi-tiered intelligent search system using:
       - ToolFinderLLM: Cost-optimized LLM-based semantic understanding with pre-filtering
       - Tool_RAG: Embedding-based similarity search
       - Keyword Search: Simple text matching as reliable fallback

    📡 **Full MCP Protocol Support**: Complete implementation of MCP specification with:
       - Standard methods (tools/list, tools/call, resources/*, prompts/*)
       - Custom scientific methods (tools/find, tools/search)
       - Multi-transport support (stdio, HTTP, SSE)
       - JSON-RPC 2.0 compliance with proper error handling

    ⚡ **High-Performance Architecture**: Production-ready features including:
       - Configurable thread pools for concurrent tool execution
       - Intelligent tool loading and caching
       - Resource management and graceful degradation
       - Comprehensive error handling and recovery

    🔧 **Developer-Friendly**: Simplified configuration and deployment with:
       - Sensible defaults for scientific computing
       - Flexible customization options
       - Comprehensive documentation and examples
       - Built-in diagnostic and monitoring tools

    Custom MCP Methods:
    ==================
    tools/find:
        AI-powered tool discovery using natural language queries. Supports semantic
        search, category filtering, and flexible response formats.

    tools/search:
        Alternative endpoint for tool discovery with identical functionality to
        tools/find, provided for compatibility and convenience.

    Parameters:
    ===========
    name : str, optional
        Human-readable server name used in logs and identification.
        Default: "SMCP Server"
        Examples: "Scientific Research API", "Drug Discovery Server"

    tooluniverse_config : ToolUniverse or dict, optional
        Either a pre-configured ToolUniverse instance or configuration dict.
        If None, creates a new ToolUniverse with default settings.
        Allows reuse of existing tool configurations and customizations.

    tool_categories : list of str, optional
        Specific ToolUniverse categories to load. If None and auto_expose_tools=True,
        loads all available tools. Common combinations:
        - Scientific: ["ChEMBL", "uniprot", "opentarget", "pubchem", "hpa"]
        - Literature: ["EuropePMC", "semantic_scholar", "pubtator", "agents"]
        - Clinical: ["fda_drug_label", "clinical_trials", "adverse_events"]

    exclude_tools : list of str, optional
        Specific tool names to exclude from loading. These tools will not be
        exposed via the MCP interface even if they are in the loaded categories.
        Useful for removing specific problematic or unwanted tools.

    exclude_categories : list of str, optional
        Tool categories to exclude from loading. These entire categories will
        be skipped during tool loading. Can be combined with tool_categories
        to first select categories and then exclude specific ones.

    include_tools : list of str, optional
        Specific tool names to include. If provided, only these tools will be
        loaded regardless of categories. Overrides category-based selection.

    tools_file : str, optional
        Path to a text file containing tool names to include (one per line).
        Alternative to include_tools parameter. Comments (lines starting with #)
        and empty lines are ignored.

    tool_config_files : dict of str, optional
        Additional tool configuration files to load. Format:
        {"category_name": "/path/to/config.json"}. These files will be loaded
        in addition to the default tool files.

    include_tool_types : list of str, optional
        Specific tool types to include. If provided, only tools of these types
        will be loaded. Available types include: 'OpenTarget', 'ToolFinderEmbedding',
        'ToolFinderKeyword', 'ToolFinderLLM', etc.

    exclude_tool_types : list of str, optional
        Tool types to exclude from loading. These tool types will be skipped
        during tool loading. Useful for excluding entire categories of tools
        (e.g., all ToolFinder types or all OpenTarget tools).

    space : str or list of str, optional
        Space configuration URI(s) to load. Can be a single URI string or a list
        of URIs for loading multiple Space configurations. Supported formats:
        - Local file: "./config.yaml" or "/path/to/config.yaml"
        - HuggingFace: "hf:username/repo" or "hf:username/repo/file.yaml"
        - HTTP URL: "https://example.com/config.yaml"

        When provided, Space configurations are loaded after tool initialization,
        applying LLM settings, hooks, and tool selections from the configuration files.
        Multiple spaces can be loaded sequentially, with later configurations
        potentially overriding earlier ones.

        Example: space="./my-workspace.yaml"
        Example: space=["hf:community/bio-tools", "./custom-tools.yaml"]

    auto_expose_tools : bool, default True
        Whether to automatically expose ToolUniverse tools as MCP tools.
        When True, all loaded tools become available via the MCP interface
        with automatic schema conversion and execution wrapping.

    search_enabled : bool, default True
        Enable AI-powered tool search functionality via tools/find method.
        Includes ToolFinderLLM (cost-optimized LLM-based), Tool_RAG (embedding-based),
        and simple keyword search capabilities with intelligent fallback.

    max_workers : int, default 5
        Maximum number of concurrent worker threads for tool execution.
        Higher values allow more parallel tool calls but use more resources.
        Recommended: 5-20 depending on server capacity and expected load.

    hooks_enabled : bool, default False
        Whether to enable output processing hooks for intelligent post-processing
        of tool outputs. When True, hooks can automatically summarize long outputs,
        save results to files, or apply other transformations.

    hook_config : dict, optional
        Custom hook configuration dictionary. If provided, overrides default
        hook settings. Should contain 'hooks' list with hook definitions.
        Example: {"hooks": [{"name": "summarization_hook", "type": "SummarizationHook", ...}]}

    hook_type : str, optional
        Simple hook type selection. Can be 'SummarizationHook', 'FileSaveHook',
        or a list of both. Provides an easy way to enable hooks without full configuration.
        Takes precedence over hooks_enabled when specified.

    **kwargs**
        Additional arguments passed to the underlying FastMCP server instance.
        Supports all FastMCP configuration options for advanced customization.

    Raises:
    =======
    ImportError
        If FastMCP is not installed. FastMCP is a required dependency for SMCP.
        Install with: pip install fastmcp

    Notes:
    ======
    - SMCP automatically handles ToolUniverse tool loading and MCP conversion
    - Tool search uses ToolFinderLLM (optimized for cost) when available, gracefully falls back to simpler methods
    - All tools support JSON argument passing for maximum flexibility
    - Server supports graceful shutdown and comprehensive resource cleanup
    - Thread pool execution ensures non-blocking operation for concurrent requests
    - Built-in error handling provides informative debugging information
    """

    def __init__(
        self,
        name: Optional[str] = None,
        tooluniverse_config: Optional[Union[ToolUniverse, Dict[str, Any]]] = None,
        tool_categories: Optional[List[str]] = None,
        exclude_tools: Optional[List[str]] = None,
        exclude_categories: Optional[List[str]] = None,
        include_tools: Optional[List[str]] = None,
        tools_file: Optional[str] = None,
        tool_config_files: Optional[Dict[str, str]] = None,
        include_tool_types: Optional[List[str]] = None,
        exclude_tool_types: Optional[List[str]] = None,
        space: Optional[Union[str, List[str]]] = None,
        auto_expose_tools: bool = True,
        search_enabled: bool = True,
        max_workers: int = 5,
        hooks_enabled: bool = False,
        hook_config: Optional[Dict[str, Any]] = None,
        hook_type: Optional[str] = None,
        **kwargs,
    ):
        if not FASTMCP_AVAILABLE:
            raise ImportError(
                "FastMCP is required for SMCP. Install it with: pip install fastmcp"
            )

        # Filter out SMCP-specific kwargs before passing to FastMCP
        fastmcp_kwargs = kwargs.copy()
        fastmcp_kwargs.pop("tooluniverse", None)  # Remove if accidentally passed

        # Initialize FastMCP with default settings optimized for scientific use
        super().__init__(name=name or "SMCP Server", **fastmcp_kwargs)

        # Get logger for this class
        self.logger = get_logger("SMCP")

        # Initialize ToolUniverse with hook support
        if isinstance(tooluniverse_config, ToolUniverse):
            self.tooluniverse = tooluniverse_config
        else:
            self.tooluniverse = ToolUniverse(
                tool_files=tooluniverse_config,
                keep_default_tools=True,
                hooks_enabled=hooks_enabled,
                hook_config=hook_config,
                hook_type=hook_type,
            )

        # Configuration
        self.tool_categories = tool_categories
        self.exclude_tools = exclude_tools or []
        self.exclude_categories = exclude_categories or []
        self.include_tools = include_tools or []
        self.tools_file = tools_file
        self.tool_config_files = tool_config_files or {}
        self.include_tool_types = include_tool_types or []
        self.exclude_tool_types = exclude_tool_types or []
        self.space = space
        self.auto_expose_tools = auto_expose_tools
        self.search_enabled = search_enabled
        self.max_workers = max_workers
        self.hooks_enabled = hooks_enabled
        self.hook_config = hook_config
        self.hook_type = hook_type

        # Space configuration storage
        self.space_llm_config = None
        self.space_metadata = None

        # Thread pool for concurrent tool execution
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # Track exposed tools to avoid duplicates
        self._exposed_tools = set()

        # Load Space configurations first if provided
        if space:
            self._load_space_configs(space)

        # Initialize SMCP-specific features (after Space is loaded)
        self._setup_smcp_tools()

        # Register custom MCP methods
        self._register_custom_mcp_methods()

    def _load_space_configs(self, space: Union[str, List[str]]):
        """
        Load Space configurations.

        This method loads Space configuration(s) and retrieves the LLM config
        and metadata from ToolUniverse. It completely reuses ToolUniverse's
        load_space functionality without reimplementing any logic.

        Args:
            space: Space URI or list of URIs (e.g., "./config.yaml",
                      "hf:user/repo", or ["config1.yaml", "config2.yaml"])
        """
        space_list = [space] if isinstance(space, str) else space

        for uri in space_list:
            print(f"📦 Loading Space: {uri}")

            # Directly call ToolUniverse's method (complete reuse)
            config = self.tooluniverse.load_space(uri)

            # Get configurations from ToolUniverse (complete reuse)
            self.space_metadata = self.tooluniverse.get_space_metadata()
            self.space_llm_config = self.tooluniverse.get_space_llm_config()

            print(f"✅ Space loaded: {config.get('name', 'Unknown')}")

    def get_llm_config(self) -> Optional[Dict[str, Any]]:
        """
        Get the current Space LLM configuration.

        Returns:
            LLM configuration dictionary or None if not set
        """
        return self.space_llm_config

    def _register_custom_mcp_methods(self):
        """
        Register custom MCP protocol methods for enhanced functionality.

        This method extends the standard MCP protocol by registering custom handlers
        for scientific tool discovery and search operations. It uses FastMCP's
        middleware system to handle custom methods while maintaining compatibility
        with standard MCP operations.

        Custom Methods Registered:
        =========================
        - tools/find: AI-powered tool discovery using natural language queries
        - tools/search: Alternative endpoint for tool search (alias for tools/find)

        Implementation Details:
        ======================
        - Uses FastMCP's middleware system instead of request handler patching
        - Implements custom middleware methods for tools/find and tools/search
        - Standard MCP methods (tools/list, tools/call) are handled by FastMCP
        - Implements proper error handling and JSON-RPC 2.0 compliance

        Notes:
        ======
        This method is called automatically during SMCP initialization and should
        not be called manually.
        """
        try:
            # Add custom middleware for tools/find and tools/search
            self.add_middleware(self._tools_find_middleware)
            self.logger.info("✅ Custom MCP methods registered successfully")

        except Exception as e:
            self.logger.error(f"Error registering custom MCP methods: {e}")

    def _get_valid_categories(self):
        """
        Get valid tool categories from ToolUniverse.

        Returns:
            Set[str]: Set of valid tool category names
        """
        try:
            # Use the existing ToolUniverse instance if available
            if hasattr(self.tooluniverse, "get_tool_types"):
                return set(self.tooluniverse.get_tool_types())
            else:
                # Create a temporary instance to get categories
                temp_tu = ToolUniverse()
                return set(temp_tu.get_tool_types())
        except Exception as e:
            self.logger.error(f"❌ Error getting valid categories: {e}")
            return set()

    async def _tools_find_middleware(self, context, call_next):
        """
        Middleware for handling tools/find and tools/search requests.

        This middleware intercepts tools/find and tools/search requests and
        provides AI-powered tool discovery functionality.
        """
        # Check if this is a tools/find or tools/search request
        if hasattr(context, "method") and context.method in [
            "tools/find",
            "tools/search",
        ]:
            try:
                # Handle the custom method
                result = await self._handle_tools_find(context.id, context.params)
                return result
            except Exception as e:
                self.logger.error(f"Error in tools/find middleware: {e}")
                return {
                    "jsonrpc": "2.0",
                    "id": context.id,
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                }

        # For all other methods, call the next middleware/handler
        return await call_next(context)

    async def _handle_tools_find(
        self, request_id: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle the tools/find MCP method for AI-powered tool discovery.

        This method implements the core functionality for the custom tools/find MCP method,
        enabling clients to discover relevant scientific tools using natural language
        queries. It supports both AI-powered semantic search and simple keyword matching.

        Parameters:
        ===========
        request_id : str
            Unique identifier for this request, used in the JSON-RPC response
        params : dict
            Request parameters containing:
            - query (required): Natural language description of desired functionality
            - categories (optional): List of tool categories to filter results
            - limit (optional): Maximum number of tools to return (default: 10)
            - use_advanced_search (optional): Whether to use AI search (default: True)
            - search_method (optional): Specific search method - 'auto', 'llm', 'embedding', 'keyword' (default: 'auto')
            - format (optional): Response format - 'detailed' or 'mcp_standard' (default: 'detailed')

        Returns:
        ========
        dict
            JSON-RPC 2.0 response containing either:
            - Success: Result with discovered tools and metadata
            - Error: Error object with appropriate code and message

        Response Formats:
        ================
        Detailed Format (default):
            Returns comprehensive tool information including:
            - Tool names, descriptions, types
            - Parameter schemas with detailed property information
            - Search metadata (query, method used, match count)

        MCP Standard Format:
            Returns tools in standard MCP tools/list format:
            - Simplified tool schema compatible with MCP clients
            - inputSchema formatted for direct MCP consumption
            - Metadata included in separate _meta field

        Search Methods:
        ==============
        AI-Powered Search (ToolFinderLLM):
            - Uses Large Language Model to understand query semantics
            - Analyzes tool descriptions for intelligent matching
            - Provides relevance scoring and reasoning
            - Automatically used when available and use_advanced_search=True

        Simple Keyword Search:
            - Basic text matching against tool names and descriptions
            - Case-insensitive substring matching
            - Used as fallback or when use_advanced_search=False

        Error Handling:
        ==============
        - Validates required parameters (query must be provided)
        - Handles search failures gracefully with informative messages
        - Provides detailed error context for debugging

        Examples:
        =========
        Basic protein analysis search:
        ```python
        params = {
            "query": "protein structure analysis",
            "limit": 3
        }
        ```

        Category-filtered drug search:
        ```python
        params = {
            "query": "drug interactions",
            "categories": ["ChEMBL", "fda_drug_label"],
            "limit": 5,
            "format": "mcp_standard"
        }
        ```
        """
        try:
            # Extract parameters
            query = params.get("query", "")
            categories = params.get("categories")
            limit = params.get("limit", 10)
            use_advanced_search = params.get("use_advanced_search", True)
            search_method = params.get(
                "search_method", "auto"
            )  # 'auto', 'llm', 'embedding', 'keyword'
            format_type = params.get(
                "format", "detailed"
            )  # 'detailed' or 'mcp_standard'

            if not query:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "Invalid params: 'query' is required",
                    },
                }

            # Perform the search using existing search functionality
            search_result = await self._perform_tool_search(
                query=query,
                categories=categories,
                limit=limit,
                use_advanced_search=use_advanced_search,
                search_method=search_method,
            )

            # Parse the search result
            search_data = json.loads(search_result)

            # Handle different response formats
            if isinstance(search_data, list):
                # If search_data is a list, treat it as tools directly
                tools_list = search_data
                search_metadata = {
                    "search_query": query,
                    "search_method": "unknown",
                    "total_matches": len(tools_list),
                    "categories_filtered": categories,
                }
            elif isinstance(search_data, dict):
                # If search_data is a dict, extract tools and metadata
                tools_list = search_data.get("tools", [])
                search_metadata = {
                    "search_query": query,
                    "search_method": search_data.get("search_method", "unknown"),
                    "total_matches": search_data.get("total_matches", len(tools_list)),
                    "categories_filtered": categories,
                }
            else:
                # Fallback for unexpected format
                tools_list = []
                search_metadata = {
                    "search_query": query,
                    "search_method": "unknown",
                    "total_matches": 0,
                    "categories_filtered": categories,
                }

            # Format response based on requested format
            if format_type == "mcp_standard":
                # Format as standard MCP tools/list style response
                mcp_tools_list = []
                for tool in tools_list:
                    mcp_tool = {
                        "name": tool.get("name"),
                        "description": tool.get("description", ""),
                        "inputSchema": {
                            "type": "object",
                            "properties": tool.get("parameters", {}),
                            "required": tool.get("required", []),
                        },
                    }
                    mcp_tools_list.append(mcp_tool)

                result = {
                    "tools": mcp_tools_list,
                    "_meta": search_metadata,
                }
            else:
                # Return detailed format (default)
                result = search_data

            return {"jsonrpc": "2.0", "id": request_id, "result": result}

        except json.JSONDecodeError as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Search result parsing error: {str(e)}",
                },
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error in tools/find: {str(e)}",
                },
            }

    async def _perform_tool_search(
        self,
        query: str,
        categories: Optional[List[str]],
        limit: int,
        use_advanced_search: bool,
        search_method: str = "auto",
    ) -> str:
        """
        Execute tool search using the most appropriate search method available.

        Simplified unified interface that leverages the consistent tool interfaces.
        All search tools now return JSON format directly.

        Parameters:
        ===========
        query : str
            Natural language query describing the desired tool functionality
        categories : list of str, optional
            Tool categories to filter results by
        limit : int
            Maximum number of tools to return
        use_advanced_search : bool
            Whether to prefer AI-powered search when available
        search_method : str, default 'auto'
            Specific search method: 'auto', 'llm', 'embedding', 'keyword'

        Returns:
        ========
        str
            JSON string containing search results
        """
        try:
            # Determine which tool to use based on method and availability
            tool_name = self._select_search_tool(search_method, use_advanced_search)

            # Prepare unified function call - all search tools now use same interface
            function_call = {
                "name": tool_name,
                "arguments": {"description": query, "limit": limit},
            }

            # Add categories only if provided to avoid validation issues
            if categories is not None:
                function_call["arguments"]["categories"] = categories

            # Execute the search tool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, self.tooluniverse.run_one_function, function_call
            )

            # All search tools now return JSON format directly
            if isinstance(result, str):
                return result
            elif isinstance(result, dict) or isinstance(result, list):
                return json.dumps(result, indent=2)
            else:
                return str(result)

        except Exception as e:
            return json.dumps(
                {
                    "error": f"Search error: {str(e)}",
                    "query": query,
                    "fallback_used": True,
                    "tools": [],
                },
                indent=2,
            )

    def _select_search_tool(self, search_method: str, use_advanced_search: bool) -> str:
        """
        Select the appropriate search tool based on method and availability.

        Returns:
            str: Tool name to use for search
        """
        # Get available tools
        all_tools = self.tooluniverse.return_all_loaded_tools()
        available_tool_names = [tool.get("name", "") for tool in all_tools]

        # Handle specific method requests
        if search_method == "keyword":
            return "Tool_Finder_Keyword"
        elif search_method == "llm" and "Tool_Finder_LLM" in available_tool_names:
            return "Tool_Finder_LLM"
        elif search_method == "embedding" and "Tool_Finder" in available_tool_names:
            return "Tool_Finder"
        elif search_method == "auto":
            # Auto-selection priority: Keyword > RAG > LLM
            if use_advanced_search:
                if "Tool_Finder_Keyword" in available_tool_names:
                    return "Tool_Finder_Keyword"
                if "Tool_Finder" in available_tool_names:
                    return "Tool_Finder"
                elif "Tool_Finder_LLM" in available_tool_names:
                    return "Tool_Finder_LLM"
        else:
            # Invalid method or method not available, fallback to keyword
            return "Tool_Finder_Keyword"

    def _setup_smcp_tools(self):
        """
        Initialize and configure SMCP-specific tools and features.

        This method orchestrates the complete setup of SMCP functionality including
        ToolUniverse tool loading, validation, automatic tool exposure to the MCP
        interface, search functionality initialization, and utility tool registration.

        The setup process is designed to be robust, handle various edge cases gracefully,
        and provide informative feedback about the configuration process. It implements
        intelligent fallback strategies to ensure functionality even when specific
        components are unavailable.

        Setup Process Overview:
        =====================
        1. **Tool Loading Assessment**: Check if ToolUniverse already has tools loaded
           to avoid unnecessary reloading and potential conflicts

        2. **Category Validation**: If specific categories are requested, validate them
           against available categories and provide helpful feedback for invalid ones

        3. **Tool Loading Strategy**: Load tools using the most appropriate method:
           - Category-specific loading for focused deployments
           - Full loading for comprehensive access
           - Graceful fallback when category loading fails

        4. **Tool Exposure**: Convert loaded ToolUniverse tools to MCP format with
           proper schema transformation and execution wrapping

        5. **Search Setup**: Initialize multi-tiered search capabilities including
           AI-powered and fallback methods

        6. **Utility Registration**: Add server management and diagnostic tools

        Tool Loading Strategy:
        =====================
        **Already Loaded Check**:
        If ToolUniverse already contains loaded tools (len(all_tools) > 0), skip
        the loading phase to prevent duplication and preserve existing configuration.
        This supports scenarios where users pre-configure ToolUniverse instances.

        **Category-Specific Loading**:
        When tool_categories is specified:
        - Validate each category against available tool categories
        - Log warnings for invalid categories with suggestions
        - Load only valid categories to optimize performance
        - Fall back to full loading if no valid categories remain

        **Full Loading (Default)**:
        When auto_expose_tools=True and no specific categories are requested,
        load all available tools to provide comprehensive functionality.

        **Graceful Fallback**:
        If category-specific loading fails for any reason, automatically
        fall back to loading all tools to ensure basic functionality.

        Tool Exposure Process:
        =====================
        **Schema Transformation**:
        - Convert ToolUniverse parameter schemas to MCP-compatible format
        - Handle complex parameter types and validation rules
        - Preserve documentation and examples where available

        **Execution Wrapping**:
        - Create async wrappers for synchronous ToolUniverse tools
        - Implement proper error handling and result formatting
        - Use thread pool execution to prevent blocking

        **Safety Mechanisms**:
        - Skip meta-tools (MCPAutoLoaderTool, MCPClientTool) that shouldn't be exposed
        - Track exposed tools to prevent duplicates
        - Handle tool conversion failures gracefully without stopping entire process

        Search Setup:
        ============
        **Multi-Tiered Search Architecture**:
        1. **ToolFinderLLM** (Primary): Cost-optimized AI-powered semantic understanding using LLM
        2. **Tool_RAG** (Secondary): Embedding-based similarity search
        3. **Keyword Search** (Fallback): Simple text matching, always available

        **Initialization Process**:
        - Check for availability of advanced search tools in loaded tools
        - Attempt to load search tools if not already present
        - Configure search capabilities based on what's available
        - Provide clear feedback about search capabilities

        **Search Tool Loading**:
        Attempts to load tool_finder_llm and tool_finder categories which include:
        - ToolFinderLLM: Cost-optimized LLM-based intelligent tool discovery
        - Tool_RAG: Embedding-based semantic search
        - Supporting utilities and configuration tools

        Error Handling:
        ==============
        **Category Validation Errors**:
        - Log specific invalid categories with available alternatives
        - Continue with valid categories only
        - Fall back to full loading if no valid categories

        **Tool Loading Errors**:
        - Log detailed error information for debugging
        - Continue setup process with already loaded tools
        - Ensure server remains functional even with partial failures

        **Search Setup Errors**:
        - Gracefully handle missing search tool dependencies
        - Fall back to simpler search methods automatically
        - Log informative messages about search capabilities

        **Tool Exposure Errors**:
        - Handle individual tool conversion failures without stopping process
        - Log specific tool errors for debugging
        - Continue with remaining tools to maximize functionality

        Performance Considerations:
        ==========================
        - **Lazy Loading**: Only load tools when needed to minimize startup time
        - **Efficient Validation**: Quick category checks before expensive operations
        - **Parallel Processing**: Use thread pools for tool conversion where possible
        - **Memory Management**: Efficient tool representation and storage

        Diagnostic Output:
        =================
        Provides informative logging throughout the setup process:
        ```
        Tools already loaded in ToolUniverse (356 tools), skipping reload
        Exposing 356 tools from ToolUniverse
        ✅ ToolFinderLLM (cost-optimized) available for advanced search
        Exposed tool: UniProt_get_entry_by_accession (type: uniprot)
        ```

        Notes:
        ======
        - This method is called automatically during SMCP initialization
        - Should not be called manually after server initialization
        - Setup is idempotent - can be called multiple times safely
        - All setup phases include comprehensive error handling
        - Performance scales with the number of tools being loaded and exposed
        """
        # Determine if ToolUniverse already has tools loaded (e.g., provided pre-configured instance)
        preloaded_tools = getattr(self.tooluniverse, "all_tools", [])
        preloaded_count = (
            len(preloaded_tools) if isinstance(preloaded_tools, list) else 0
        )

        if preloaded_count > 0:
            self.logger.info(
                f"ToolUniverse already pre-configured with {preloaded_count} tool(s); skipping automatic loading."
            )

        # Check if Space has already loaded specific tools
        if (
            self.space
            and hasattr(self.tooluniverse, "_current_space_config")
            and preloaded_count > 0
        ):
            # Space has already loaded specific tools, don't reload all tools
            self.logger.info(
                f"Space configuration loaded {preloaded_count} tool(s), skipping additional loading"
            )
        elif preloaded_count == 0 and self.tool_categories:
            try:
                # Validate categories first
                valid_categories = self._get_valid_categories()
                invalid_categories = [
                    cat for cat in self.tool_categories if cat not in valid_categories
                ]

                if invalid_categories:
                    available_categories = list(valid_categories)
                    self.logger.warning(
                        f"Invalid categories {invalid_categories}. Available categories: {available_categories}"
                    )
                    # Filter to valid categories only
                    valid_only = [
                        cat for cat in self.tool_categories if cat in valid_categories
                    ]
                    if valid_only:
                        self.logger.info(f"Loading valid categories: {valid_only}")
                        self.tooluniverse.load_tools(
                            tool_type=valid_only,
                            exclude_tools=self.exclude_tools,
                            exclude_categories=self.exclude_categories,
                            include_tools=self.include_tools,
                            tools_file=self.tools_file,
                            tool_config_files=self.tool_config_files,
                            include_tool_types=self.include_tool_types,
                            exclude_tool_types=self.exclude_tool_types,
                        )
                    else:
                        self.logger.warning(
                            "No valid categories found, loading all tools instead"
                        )
                        self.tooluniverse.load_tools(
                            exclude_tools=self.exclude_tools,
                            exclude_categories=self.exclude_categories,
                            include_tools=self.include_tools,
                            tools_file=self.tools_file,
                            tool_config_files=self.tool_config_files,
                            include_tool_types=self.include_tool_types,
                            exclude_tool_types=self.exclude_tool_types,
                        )
                else:
                    self.tooluniverse.load_tools(
                        tool_type=self.tool_categories,
                        exclude_tools=self.exclude_tools,
                        exclude_categories=self.exclude_categories,
                        include_tools=self.include_tools,
                        tools_file=self.tools_file,
                        tool_config_files=self.tool_config_files,
                        include_tool_types=self.include_tool_types,
                        exclude_tool_types=self.exclude_tool_types,
                    )
            except Exception as e:
                self.logger.error(f"Error loading specified categories: {e}")
                self.logger.info("Falling back to loading all tools")
                self.tooluniverse.load_tools(
                    exclude_tools=self.exclude_tools,
                    exclude_categories=self.exclude_categories,
                    include_tools=self.include_tools,
                    tools_file=self.tools_file,
                    tool_config_files=self.tool_config_files,
                    include_tool_types=self.include_tool_types,
                    exclude_tool_types=self.exclude_tool_types,
                )
        elif self.auto_expose_tools and not (
            self.space and hasattr(self.tooluniverse, "_current_space_config")
        ):
            # Load all tools by default (unless Space already handled tool loading)
            self.tooluniverse.load_tools(
                exclude_tools=self.exclude_tools,
                exclude_categories=self.exclude_categories,
                include_tools=self.include_tools,
                tools_file=self.tools_file,
                tool_config_files=self.tool_config_files,
                include_tool_types=self.include_tool_types,
                exclude_tool_types=self.exclude_tool_types,
            )

        # Auto-expose ToolUniverse tools as MCP tools
        if self.auto_expose_tools:
            self._expose_tooluniverse_tools()

        # Add search functionality if enabled
        if self.search_enabled:
            self._add_search_tools()

        # Add utility tools
        self._add_utility_tools()

    def _expose_tooluniverse_tools(self):
        """
        Automatically expose ToolUniverse tools as MCP-compatible tools.

        This method performs the critical task of converting ToolUniverse's tool
        definitions into FastMCP-compatible tools that can be called via the MCP
        protocol. It handles the complex mapping between different tool formats
        while ensuring compatibility and usability.

        Process Overview:
        ================
        1. **Tool Inventory**: Enumerate all loaded ToolUniverse tools
        2. **Type Filtering**: Skip meta-tools that shouldn't be exposed
        3. **Schema Conversion**: Transform ToolUniverse schemas to MCP format
        4. **Function Wrapping**: Create async wrappers for tool execution
        5. **Registration**: Register tools with FastMCP framework

        Tool Type Filtering:
        ===================
        Skips these internal tool types:
        - MCPAutoLoaderTool: Used for loading other MCP servers
        - MCPClientTool: Used for connecting to external MCP servers

        These are meta-tools that manage other tools rather than providing
        end-user functionality, so they're excluded from the MCP interface.

        Schema Transformation:
        =====================
        ToolUniverse Tool Format:
        ```json
        {
            "name": "tool_name",
            "parameter": {
                "type": "object",
                "properties": {...},
                "required": [...]
            }
        }
        ```

        MCP Tool Format:
        ```python
        async def tool_function(arguments: str = "{}") -> str:
            # Tool execution logic
        ```

        Execution Model:
        ===============
        - **JSON Arguments**: All tools accept a single 'arguments' parameter
          containing JSON-encoded tool parameters
        - **Async Execution**: Tools run in thread pool to prevent blocking
        - **Error Handling**: Comprehensive error catching and reporting
        - **Type Safety**: Proper argument parsing and validation

        Duplicate Prevention:
        ====================
        - Tracks exposed tools in self._exposed_tools set
        - Prevents re-registration of already exposed tools
        - Handles tool reloading scenarios gracefully

        Error Recovery:
        ==============
        - Individual tool failures don't stop the entire process
        - Detailed error logging for debugging
        - Continues with remaining tools if some fail to convert

        Performance Optimization:
        ========================
        - Lazy evaluation of tool schemas
        - Minimal memory footprint per tool
        - Efficient tool lookup and execution
        - Thread pool reuse for all tool executions

        Examples:
        =========
        Original ToolUniverse tool call:
        ```python
        tu.run_one_function({
            "name": "UniProt_get_entry_by_accession",
            "arguments": {"accession": "P05067"}
        })
        ```

        Equivalent MCP tool call:
        ```python
        await tool_function('{"accession": "P05067"}')
        ```
        """
        if not hasattr(self.tooluniverse, "all_tools"):
            self.logger.warning("No all_tools attribute in tooluniverse")
            return

        self.logger.info(
            f"Exposing {len(self.tooluniverse.all_tools)} tools from ToolUniverse"
        )

        # Define tool types that should not be exposed as MCP tools
        # These are internal/meta tools that are used for loading other tools
        skip_tool_types = {"MCPAutoLoaderTool", "MCPClientTool"}

        for i, tool_config in enumerate(self.tooluniverse.all_tools):
            try:
                # Debug: Check the type of tool_config
                if not isinstance(tool_config, dict):
                    self.logger.warning(
                        f"tool_config at index {i} is not a dict, it's {type(tool_config)}: {tool_config}"
                    )
                    continue

                tool_name = tool_config.get("name")
                tool_type = tool_config.get("type")

                # Skip internal/meta tools that are used for loading other tools
                if tool_type in skip_tool_types:
                    self.logger.debug(
                        f"Skipping exposure of meta tool: {tool_name} (type: {tool_type})"
                    )
                    continue

                if tool_name and tool_name not in self._exposed_tools:
                    self._create_mcp_tool_from_tooluniverse(tool_config)
                    self._exposed_tools.add(tool_name)
                    self.logger.debug(f"Exposed tool: {tool_name} (type: {tool_type})")

            except Exception as e:
                self.logger.error(f"Error processing tool at index {i}: {e}")
                self.logger.debug(f"Tool config: {tool_config}")
                continue

        exposed_count = len(self._exposed_tools)
        self.logger.info(f"Successfully exposed {exposed_count} tools to MCP interface")

    def _add_search_tools(self):
        """
        Register AI-powered tool search and discovery functionality.

        This method adds sophisticated tool discovery capabilities to the SMCP server,
        enabling clients to find relevant tools using natural language queries.
        It provides both programmatic (MCP tool) and protocol-level (tools/find method)
        interfaces for tool discovery.

        Registered Tools:
        ================

        find_tools:
            Primary tool discovery interface with AI-powered search capabilities.

            Parameters:
            - query (str): Natural language description of desired functionality
            - categories (list, optional): Tool categories to filter by
            - limit (int, default=10): Maximum number of results
            - use_advanced_search (bool, default=True): Use AI vs keyword search

            Returns: JSON string with discovered tools and search metadata

        search_tools:
            Backward-compatible alias for find_tools with identical functionality.
            Maintained for compatibility with existing integrations.

        Search Capabilities:
        ===================

        AI-Powered Search (ToolFinderLLM):
            - Uses Large Language Model to understand query semantics with optimized context
            - Pre-filters tools using keyword matching to reduce LLM context cost
            - Analyzes only essential tool information (name + description) for cost efficiency
            - Provides relevance scoring and reasoning
            - Handles complex queries like "analyze protein interactions in cancer"

        Embedding-Based Search (Tool_RAG):
            - Uses vector embeddings for semantic similarity matching
            - Fast approximate matching for large tool collections
            - Good balance between speed and semantic understanding

        Keyword Search (Fallback):
            - Simple text matching against tool names and descriptions
            - Always available regardless of AI tool availability
            - Provides basic but reliable tool discovery

        Search Strategy:
        ===============
        1. **Preference**: ToolFinderLLM (most intelligent, cost-optimized)
        2. **Fallback**: Tool_RAG (semantic similarity)
        3. **Final**: Simple keyword matching (always works)

        Integration Details:
        ===================
        - Automatically initializes available search tools during setup
        - Shares search logic with tools/find MCP method
        - Provides consistent results across different interfaces
        - Handles tool loading and availability detection

        Error Handling:
        ==============
        - Graceful degradation when AI tools unavailable
        - Informative error messages for debugging
        - Fallback mechanisms ensure search always works
        - Detailed logging of search method selection

        Usage Examples:
        ==============
        Via MCP tool interface:
        ```python
        result = await find_tools(
            query="protein structure prediction",
            categories=["uniprot", "hpa"],
            limit=5
        )
        ```

        Via tools/find MCP method:
        ```json
        {
            "method": "tools/find",
            "params": {
                "query": "drug interaction analysis",
                "limit": 3
            }
        }
        ```
        """

        # Initialize tool finder (prefer LLM-based if available, fallback to embedding-based)
        self._init_tool_finder()

        @self.tool()
        async def find_tools(
            query: str,
            categories: Optional[List[str]] = None,
            limit: int = 10,
            use_advanced_search: bool = True,
            search_method: str = "auto",
        ) -> str:
            """
            Find and search available ToolUniverse tools using AI-powered search.

            This tool provides the same functionality as the tools/find MCP method.

            Args:
                query: Search query describing the desired functionality
                categories: Optional list of categories to filter by
                limit: Maximum number of results to return (default: 10)
                use_advanced_search: Use AI-powered search if available (default: True)
                search_method: Specific search method - 'auto', 'llm', 'embedding', 'keyword' (default: 'auto')

            Returns:
                JSON string containing matching tools with detailed information
            """
            return await self._perform_tool_search(
                query, categories, limit, use_advanced_search, search_method
            )

        # # Keep the original search_tools as an alias for backward compatibility
        # @self.tool()
        # async def search_tools(
        #     query: str,
        #     categories: Optional[List[str]] = None,
        #     limit: int = 10,
        #     use_advanced_search: bool = True,
        #     search_method: str = 'auto'
        # ) -> str:
        #     """
        #     Search available ToolUniverse tools (alias for find_tools).

        #     Args:
        #         query: Search query string describing the desired functionality
        #         categories: Optional list of categories to filter by
        #         limit: Maximum number of results to return
        #         use_advanced_search: Whether to use AI-powered tool finder
        #         search_method: Specific search method - 'auto', 'llm', 'embedding', 'keyword' (default: 'auto')

        #     Returns:
        #         JSON string containing matching tools information
        #     """
        #     return await self._perform_tool_search(query, categories, limit, use_advanced_search, search_method)

    def _init_tool_finder(self):
        """
        Initialize intelligent tool discovery system with automatic fallback.

        This method sets up the tool finder infrastructure that powers AI-driven
        tool discovery. It implements a tiered approach, trying the most advanced
        search methods first and falling back to simpler methods if needed.

        Initialization Strategy:
        =======================

        Phase 1 - Detection:
            Scans loaded ToolUniverse tools to identify available search tools:
            - ToolFinderLLM: Advanced LLM-based semantic search
            - Tool_RAG: Embedding-based similarity search

        Phase 2 - Loading (if needed):
            If no search tools are found, attempts to load them:
            - Loads 'tool_finder_llm' and 'tool_finder' categories
            - Re-scans for available tools after loading

        Phase 3 - Selection:
            Selects the best available search method:
            1. ToolFinderLLM (preferred - most intelligent)
            2. Tool_RAG (fallback - good semantic understanding)
            3. Simple keyword search (always available)

        Tool Finder Capabilities:
        ========================

        ToolFinderLLM:
            - Uses GPT-4 or similar LLM for query understanding
            - Analyzes tool descriptions for semantic matching
            - Provides relevance scoring and selection reasoning
            - Handles complex, multi-faceted queries effectively
            - Best for: "Find tools to analyze protein-drug interactions in cancer research"

        Tool_RAG:
            - Uses pre-computed embeddings for fast similarity search
            - Good semantic understanding without LLM overhead
            - Faster than LLM-based search for simple queries
            - Best for: "protein analysis", "drug discovery"

        Simple Search:
            - Basic keyword matching against names and descriptions
            - No dependencies, always available
            - Fast and reliable for exact term matches
            - Best for: "chembl", "uniprot", "fda"

        Configuration Management:
        ========================
        Sets instance attributes:
        - tool_finder_available (bool): Whether advanced search is available
        - tool_finder_type (str): Type of search tool loaded ("ToolFinderLLM" | "Tool_RAG")

        Error Handling:
        ==============
        - Handles missing dependencies gracefully
        - Provides informative console output about search capabilities
        - Ensures search functionality always works (via simple fallback)
        - Logs detailed information for debugging

        Performance Considerations:
        ==========================
        - Tool loading only happens if search tools aren't already available
        - Search tool detection is cached to avoid repeated scans
        - ToolFinderLLM requires network access and API keys
        - Tool_RAG requires embedding files but works offline

        Dependencies:
        ============
        - ToolFinderLLM: Requires OpenAI API access or compatible endpoint
        - Tool_RAG: Requires sentence-transformers and embedding data
        - Simple search: No external dependencies
        """
        self.tool_finder_available = False
        self.tool_finder_type = None

        # Check if ToolFinderLLM is available in loaded tools
        try:
            all_tools = self.tooluniverse.return_all_loaded_tools()
            available_tool_names = [tool.get("name", "") for tool in all_tools]

            # Try ToolFinderLLM first (more advanced)
            if "Tool_Finder_LLM" in available_tool_names:
                self.tool_finder_available = True
                self.tool_finder_type = "Tool_Finder_LLM"
                self.logger.info("✅ Tool_Finder_LLM available for advanced search")
                return

            # Fallback to Tool_RAG (embedding-based)
            if "Tool_RAG" in available_tool_names:
                self.tool_finder_available = True
                self.tool_finder_type = "Tool_RAG"
                self.logger.info(
                    "✅ Tool_RAG (embedding-based) available for advanced search"
                )
                return

            # Check if ToolFinderKeyword is available for simple search
            if "Tool_Finder_Keyword" in available_tool_names:
                self.logger.info("✅ ToolFinderKeyword available for simple search")

            self.logger.warning("⚠️ No advanced tool finders available in loaded tools")
            self.logger.debug(
                f"Available tools: {available_tool_names[:5]}..."
            )  # Show first 5 tools

        except Exception as e:
            self.logger.warning(f"⚠️ Failed to check for tool finders: {e}")

        # Try to load tool finder tools if not already loaded
        try:
            self.logger.debug("🔄 Attempting to load tool finder tools...")

            # Load tool_finder category which includes ToolFinderLLM, Tool_RAG, and ToolFinderKeyword
            self.tooluniverse.load_tools(tool_type=["tool_finder"])

            # Re-check availability
            all_tools = self.tooluniverse.return_all_loaded_tools()
            available_tool_names = [tool.get("name", "") for tool in all_tools]

            if "Tool_Finder_LLM" in available_tool_names:
                self.tool_finder_available = True
                self.tool_finder_type = "Tool_Finder_LLM"
                self.logger.info(
                    "✅ Successfully loaded Tool_Finder_LLM for advanced search"
                )
            elif "Tool_RAG" in available_tool_names:
                self.tool_finder_available = True
                self.tool_finder_type = "Tool_RAG"
                self.logger.info("✅ Successfully loaded Tool_RAG for advanced search")
            else:
                self.logger.warning("⚠️ Failed to load any advanced tool finder tools")

            # Check if ToolFinderKeyword is available for simple search
            if "Tool_Finder_Keyword" in available_tool_names:
                self.logger.info("✅ Tool_Finder_Keyword available for simple search")
            else:
                self.logger.warning(
                    "⚠️ ToolFinderKeyword not available, using fallback search"
                )

        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load tool finder tools: {e}")
            self.logger.info(
                "📝 Advanced search will not be available, using simple keyword search only"
            )

    def _add_utility_tools(self):
        """
        Register essential server management and diagnostic tools.

        This method adds a suite of utility tools that provide server introspection,
        tool management, and direct execution capabilities. These tools are essential
        for monitoring server health, understanding available capabilities, and
        providing administrative functionality.

        Registered Utility Tools:
        ========================

        get_server_info:
            Comprehensive server status and capability reporting.

            Returns detailed JSON with:
            - Server identification (name, type, version info)
            - Tool statistics (total tools, exposed tools, categories)
            - Feature flags (search enabled, FastMCP status)
            - Resource usage (max workers, thread pool status)

            Use cases:
            - Health checks and monitoring
            - Capability discovery by clients
            - Debugging server configuration issues

        execute_tooluniverse_function:
            Direct interface for executing ToolUniverse functions with custom parameters.

            Parameters:
            - function_name (str): Name of the ToolUniverse tool to execute
            - arguments (str): JSON string containing tool parameters

            Features:
            - Bypasses MCP tool wrappers for direct execution
            - Supports any loaded ToolUniverse tool
            - Provides detailed error reporting
            - Uses thread pool for non-blocking execution

            Use cases:
            - Administrative tool execution
            - Debugging tool behavior
            - Custom automation scripts

        list_available_tooluniverse_tools:
            Comprehensive inventory of all available ToolUniverse tools.

            Returns:
            - Complete tool catalog with names, descriptions, types
            - Parameter schemas and requirements for each tool
            - Tool statistics and categorization

            Use cases:
            - Tool discovery and exploration
            - Documentation generation
            - Client capability mapping
            - Integration planning

        Implementation Details:
        ======================

        Error Handling:
            - Each tool includes comprehensive try-catch blocks
            - Detailed error messages with context information
            - Graceful degradation when tools or data unavailable
            - JSON-formatted error responses for consistency

        Thread Safety:
            - All tools use async execution patterns
            - Thread pool executor for CPU-intensive operations
            - Proper resource cleanup and management
            - Non-blocking I/O for network operations

        Security Considerations:
            - execute_tooluniverse_function provides direct tool access
            - JSON parsing with proper validation
            - No file system access beyond ToolUniverse scope
            - Appropriate error message sanitization

        Performance Optimization:
            - Lazy loading of tool information
            - Caching where appropriate
            - Minimal memory footprint
            - Efficient JSON serialization

        Examples:
        =========

        Server health check:
        ```python
        info = await get_server_info()
        status = json.loads(info)
        if status['total_tooluniverse_tools'] > 0:
            # Server healthy
            pass
        ```

        Direct tool execution:
        ```python
        result = await execute_tooluniverse_function(
            function_name="UniProt_get_entry_by_accession",
            arguments='{"accession": "P05067"}'
        )
        ```

        Tool inventory:
        ```python
        tools = await list_available_tooluniverse_tools()
        catalog = json.loads(tools)
        # Available: {catalog['total_tools']} tools
        ```
        """

        @self.tool()
        async def get_server_info() -> str:
            """
            Get information about the SMCP server and its capabilities.

            Returns:
                JSON string containing server information
            """
            try:
                info = {
                    "server_name": self.name,
                    "server_type": "SMCP (Scientific Model Context Protocol)",
                    "fastmcp_available": FASTMCP_AVAILABLE,
                    "tooluniverse_loaded": hasattr(self, "tooluniverse"),
                    "total_exposed_tools": len(self._exposed_tools),
                    "search_enabled": self.search_enabled,
                    "max_workers": self.max_workers,
                    "tool_categories_loaded": len(
                        getattr(self.tooluniverse, "tool_category_dicts", {})
                    ),
                    "total_tooluniverse_tools": len(
                        getattr(self.tooluniverse, "all_tools", [])
                    ),
                }
                return json.dumps(info, indent=2)

            except Exception as e:
                return f"Error getting server info: {str(e)}"

        @self.tool()
        async def execute_tooluniverse_function(
            function_name: str, arguments: str
        ) -> str:
            """
            Execute a ToolUniverse function directly with custom arguments.

            Args:
                function_name: Name of the ToolUniverse function to execute
                arguments: JSON string of arguments to pass to the function

            Returns:
                Function execution result
            """
            try:
                # Parse arguments from JSON string
                import json

                if isinstance(arguments, str):
                    parsed_args = json.loads(arguments)
                else:
                    parsed_args = arguments

                function_call = {"name": function_name, "arguments": parsed_args}

                # Execute in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor, self.tooluniverse.run_one_function, function_call
                )

                return str(result)

            except Exception as e:
                return f"Error executing {function_name}: {str(e)}"

        @self.tool()
        async def list_available_tooluniverse_tools() -> str:
            """
            List all available ToolUniverse tools that can be executed.

            Returns:
                JSON string containing available tools and their descriptions
            """
            try:
                # Check if ToolUniverse has loaded tools
                if (
                    not hasattr(self.tooluniverse, "all_tools")
                    or not self.tooluniverse.all_tools
                ):
                    return json.dumps({"error": "No ToolUniverse tools loaded"})

                tools_info = []
                for tool_config in self.tooluniverse.all_tools:
                    if isinstance(tool_config, dict):
                        tool_info = {
                            "name": tool_config.get("name", "Unknown"),
                            "description": tool_config.get(
                                "description", "No description available"
                            ),
                            "type": tool_config.get("type", "Unknown"),
                            "parameter_schema": tool_config.get("parameter", {}),
                        }
                        tools_info.append(tool_info)

                return json.dumps(
                    {"total_tools": len(tools_info), "tools": tools_info}, indent=2
                )

            except Exception as e:
                return json.dumps({"error": f"Error listing tools: {str(e)}"}, indent=2)

    def add_custom_tool(
        self, name: str, function: Callable, description: Optional[str] = None, **kwargs
    ):
        """
        Add a custom Python function as an MCP tool to the SMCP server.

        This method provides a convenient way to extend SMCP functionality with
        custom tools beyond those provided by ToolUniverse. Custom tools are
        automatically integrated into the MCP interface and can be discovered
        and used by clients alongside existing tools.

        Parameters:
        ===========
        name : str
            Unique name for the tool in the MCP interface. Should be descriptive
            and follow naming conventions (lowercase with underscores preferred).
            Examples: "analyze_protein_sequence", "custom_data_processor"

        function : Callable
            Python function to execute when the tool is called. The function:
            - Can be synchronous or asynchronous
            - Should have proper type annotations for parameters
            - Should include a comprehensive docstring
            - Will be automatically wrapped for MCP compatibility

        description : str, optional
            Human-readable description of the tool's functionality. If provided,
            this will be set as the function's __doc__ attribute. If None, the
            function's existing docstring will be used.

        **kwargs**
            Additional FastMCP tool configuration options:
            - parameter_schema: Custom JSON schema for parameters
            - return_schema: Schema for return values
            - examples: Usage examples for the tool
            - tags: Categorization tags

        Returns:
        ========
        Callable
            The decorated function registered with FastMCP framework.

        Usage Examples:
        ==============

        Simple synchronous function:
        ```python
        def analyze_text(text: str, max_length: int = 100) -> str:
            '''Analyze text and return summary.'''
            return text[:max_length] + "..." if len(text) > max_length else text

        server.add_custom_tool(
            name="text_analyzer",
            function=analyze_text,
            description="Analyze and summarize text content"
        )
        ```

        Asynchronous function with complex parameters:
        ```python
        async def process_data(
            data: List[Dict[str, Any]],
            processing_type: str = "standard"
        ) -> Dict[str, Any]:
            '''Process scientific data with specified method.'''
            # Custom processing logic here
            return {"processed_items": len(data), "type": processing_type}

        server.add_custom_tool(
            name="data_processor",
            function=process_data
        )
        ```

        Function with custom schema:
        ```python
        def calculate_score(values: List[float]) -> float:
            '''Calculate composite score from values.'''
            return sum(values) / len(values) if values else 0.0

        server.add_custom_tool(
            name="score_calculator",
            function=calculate_score,
            parameter_schema={
                "type": "object",
                "properties": {
                    "values": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "List of numeric values to process"
                    }
                },
                "required": ["values"]
            }
        )
        ```

        Integration with ToolUniverse:
        =============================
        Custom tools work seamlessly alongside ToolUniverse tools:
        - Appear in tool discovery searches
        - Follow same calling conventions
        - Include in server diagnostics and listings
        - Support all MCP client interaction patterns

        Best Practices:
        ===============
        - Use descriptive, unique tool names
        - Include comprehensive docstrings
        - Add proper type annotations for parameters
        - Handle errors gracefully within the function
        - Consider async functions for I/O-bound operations
        - Test tools thoroughly before deployment

        Notes:
        ======
        - Custom tools are registered immediately upon addition
        - Tools can be added before or after server startup
        - Function signature determines parameter schema automatically
        - Custom tools support all FastMCP features and conventions
        """
        if description:
            function.__doc__ = description

        # Use FastMCP's tool decorator
        decorated_function = self.tool(name=name, **kwargs)(function)
        return decorated_function

    async def close(self):
        """
        Perform comprehensive cleanup and resource management during server shutdown.

        This method ensures graceful shutdown of the SMCP server by properly cleaning
        up all resources, stopping background tasks, and releasing system resources.
        It's designed to be safe to call multiple times and handles errors gracefully.

        Cleanup Operations:
        ===================

        **Thread Pool Shutdown:**
        - Gracefully stops the ThreadPoolExecutor used for tool execution
        - Waits for currently running tasks to complete
        - Prevents new tasks from being submitted
        - Times out after reasonable wait period to prevent hanging

        **Resource Cleanup:**
        - Releases any open file handles or network connections
        - Clears internal caches and temporary data
        - Stops background monitoring tasks
        - Frees memory allocated for tool configurations

        **Error Handling:**
        - Continues cleanup even if individual operations fail
        - Logs cleanup errors for debugging without raising exceptions
        - Ensures critical resources are always released

        Usage Patterns:
        ===============

        **Automatic Cleanup (Recommended):**
        ```python
        server = SMCP("My Server")
        try:
            server.run_simple()  # Cleanup happens automatically on exit
        except KeyboardInterrupt:
            pass  # run_simple() handles cleanup
        ```

        **Manual Cleanup:**
        ```python
        server = SMCP("My Server")
        try:
            # Custom server logic here
            pass
        finally:
            await server.close()  # Explicit cleanup
        ```

        **Context Manager Pattern:**
        ```python
        async with SMCP("My Server") as server:
            # Server operations
            pass
        # Cleanup happens automatically
        ```

        Performance Considerations:
        ===========================
        - Cleanup operations are typically fast (< 1 second)
        - Thread pool shutdown may take longer if tasks are running
        - Network connections are closed immediately
        - Memory cleanup depends on garbage collection

        Error Recovery:
        ===============
        - Individual cleanup failures don't stop the overall process
        - Critical errors are logged but don't raise exceptions
        - Cleanup is idempotent - safe to call multiple times
        - System resources are guaranteed to be released

        Notes:
        ======
        - This method is called automatically by run_simple() on shutdown
        - Can be called manually for custom server lifecycle management
        - Async method to properly handle async resource cleanup
        - Safe to call even if server hasn't been fully initialized
        """
        try:
            # Shutdown thread pool
            self.executor.shutdown(wait=True)
        except Exception:
            pass

    def _print_tooluniverse_banner(self):
        """Print ToolUniverse branding banner after FastMCP banner with dynamic information."""
        # Get transport info if available
        transport_display = getattr(self, "_transport_type", "Unknown")
        server_url = getattr(self, "_server_url", "N/A")
        tools_count = len(self._exposed_tools)

        # Map transport types to display names
        transport_map = {
            "stdio": "STDIO",
            "streamable-http": "Streamable-HTTP",
            "http": "HTTP",
            "sse": "SSE",
        }
        transport_name = transport_map.get(transport_display, transport_display)

        # Format lines with proper alignment (matching FastMCP style)
        # Each line should be exactly 75 characters (emoji takes 2 display widths but counts as 1 in len())
        transport_line = f"                 📦 Transport:       {transport_name}"
        server_line = f"                 🔗 Server URL:      {server_url}"
        tools_line = f"                 🧰 Loaded Tools:    {tools_count}"

        # Pad to exactly 75 characters (emoji counts as 1 in len() but displays as 2)
        transport_line = transport_line + " " * (75 - len(transport_line))
        server_line = server_line + " " * (75 - len(server_line))
        tools_line = tools_line + " " * (75 - len(tools_line))

        banner = f"""
╭────────────────────────────────────────────────────────────────────────────╮
│                                                                            │
│                         🧬 ToolUniverse SMCP Server 🧬                     │
│                                                                            │
│            Bridging AI Agents with Scientific Computing Tools              │
│                                                                            │
│{transport_line}│
│{server_line}│
│{tools_line}│
│                                                                            │
│                 🌐 Website:  https://aiscientist.tools/                    │
│                 💻 GitHub:   https://github.com/mims-harvard/ToolUniverse  │
│                                                                            │
╰────────────────────────────────────────────────────────────────────────────╯
"""
        # In stdio mode, ensure the banner goes to stderr to avoid polluting stdout
        # which must exclusively carry JSON-RPC messages.
        import sys as _sys

        if getattr(self, "_transport_type", None) == "stdio":
            print(banner, file=_sys.stderr)
        else:
            print(banner)

    def run(self, *args, **kwargs):
        """
        Override run method to display ToolUniverse banner after FastMCP banner.

        This method intercepts the parent's run() call to inject our custom banner
        immediately after FastMCP displays its startup banner.
        """
        # Save transport information for banner display
        transport = kwargs.get("transport", args[0] if args else "unknown")
        host = kwargs.get("host", "0.0.0.0")
        port = kwargs.get("port", 7000)

        self._transport_type = transport

        # Build server URL based on transport
        if transport == "streamable-http" or transport == "http":
            self._server_url = f"http://{host}:{port}/mcp"
        elif transport == "sse":
            self._server_url = f"http://{host}:{port}"
        else:
            self._server_url = "N/A (stdio mode)"

        # Use threading to print our banner shortly after FastMCP's banner
        import threading
        import time

        def delayed_banner():
            """Print ToolUniverse banner with a small delay to appear after FastMCP banner."""
            time.sleep(1.0)  # Delay to ensure FastMCP banner displays first
            self._print_tooluniverse_banner()

        # Start banner thread only on first run
        if not hasattr(self, "_tooluniverse_banner_shown"):
            self._tooluniverse_banner_shown = True
            banner_thread = threading.Thread(target=delayed_banner, daemon=True)
            banner_thread.start()

        # Call parent's run method (blocking call)
        return super().run(*args, **kwargs)

    def run_simple(
        self,
        transport: Literal["stdio", "http", "sse"] = "http",
        host: str = "0.0.0.0",
        port: int = 7000,
        **kwargs,
    ):
        """
        Start the SMCP server with simplified configuration and automatic setup.

        This method provides a convenient way to launch the SMCP server with sensible
        defaults for different deployment scenarios. It handles transport configuration,
        logging setup, and graceful shutdown automatically.

        Parameters:
        ===========
        transport : {"stdio", "http", "sse"}, default "http"
            Communication transport protocol:

            - "stdio": Standard input/output communication
              * Best for: Command-line tools, subprocess integration
              * Pros: Low overhead, simple integration
              * Cons: Single client, no network access

            - "http": HTTP-based communication (streamable-http)
              * Best for: Web applications, REST API integration
              * Pros: Wide compatibility, stateless, scalable
              * Cons: Higher overhead than stdio

            - "sse": Server-Sent Events over HTTP
              * Best for: Real-time applications, streaming responses
              * Pros: Real-time communication, web-compatible
              * Cons: Browser limitations, more complex

        host : str, default "0.0.0.0"
            Server bind address for HTTP/SSE transports:
            - "0.0.0.0": Listen on all network interfaces (default)
            - "127.0.0.1": localhost only (more secure)
            - Specific IP: Bind to particular interface

        port : int, default 7000
            Server port for HTTP/SSE transports. Choose ports:
            - 7000-7999: Recommended range for SMCP servers
            - Above 1024: No root privileges required
            - Check availability: Ensure port isn't already in use

        **kwargs**
            Additional arguments passed to FastMCP's run() method:
            - debug (bool): Enable debug logging
            - access_log (bool): Log client requests
            - workers (int): Number of worker processes (HTTP only)

        Server Startup Process:
        =======================
        1. **Initialization Summary**: Displays server configuration and capabilities
        2. **Transport Setup**: Configures selected communication method
        3. **Service Start**: Begins listening for client connections
        4. **Graceful Shutdown**: Handles interrupts and cleanup

        Deployment Scenarios:
        =====================

        Development & Testing:
        ```python
        server = SMCP(name="Dev Server")
        server.run_simple(transport="stdio")  # For CLI testing
        ```

        Local Web Service:
        ```python
        server = SMCP(name="Local API")
        server.run_simple(transport="http", host="127.0.0.1", port=8000)
        ```

        Production Service:
        ```python
        server = SMCP(
            name="Production SMCP",
            tool_categories=["ChEMBL", "uniprot", "opentarget"],
            max_workers=20
        )
        server.run_simple(
            transport="http",
            host="0.0.0.0",
            port=7000,
            workers=4
        )
        ```

        Real-time Applications:
        ```python
        server = SMCP(name="Streaming API")
        server.run_simple(transport="sse", port=7001)
        ```

        Error Handling:
        ===============
        - **KeyboardInterrupt**: Graceful shutdown on Ctrl+C
        - **Port in Use**: Clear error message with suggestions
        - **Transport Errors**: Detailed debugging information
        - **Cleanup**: Automatic resource cleanup on exit

        Logging Output:
        ===============
        Provides informative startup messages:
        ```
        🚀 Starting SMCP server 'My Server'...
        📊 Loaded 356 tools from ToolUniverse
        🔍 Search enabled: True
        🌐 Server running on http://0.0.0.0:7000
        ```

        Security Considerations:
        ========================
        - Use host="127.0.0.1" for local-only access
        - Configure firewall rules for production deployment
        - Consider HTTPS termination with reverse proxy
        - Validate all client inputs through MCP protocol

        Performance Notes:
        ==================
        - HTTP transport supports multiple concurrent clients
        - stdio transport is single-client but lower latency
        - SSE transport enables real-time bidirectional communication
        - Thread pool size affects concurrent tool execution capacity
        """
        self.logger.info(f"🚀 Starting SMCP server '{self.name}'...")
        self.logger.info(
            f"📊 Loaded {len(self._exposed_tools)} tools from ToolUniverse"
        )
        self.logger.info(f"🔍 Search enabled: {self.search_enabled}")

        # Log hook configuration
        if self.hooks_enabled or self.hook_type:
            if self.hook_type:
                self.logger.info(f"🔗 Hooks enabled: {self.hook_type}")
            elif self.hook_config:
                hook_count = len(self.hook_config.get("hooks", []))
                self.logger.info(f"🔗 Hooks enabled: {hook_count} custom hooks")
            else:
                self.logger.info("🔗 Hooks enabled: default configuration")
        else:
            self.logger.info("🔗 Hooks disabled")

        # Configure logger for stdio mode to avoid stdout pollution
        if transport == "stdio":
            import logging
            import sys

            # Redirect all logger output to stderr for stdio mode
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)

            stderr_handler = logging.StreamHandler(sys.stderr)
            stderr_handler.setLevel(logging.INFO)
            formatter = logging.Formatter("%(message)s")
            stderr_handler.setFormatter(formatter)
            self.logger.addHandler(stderr_handler)
            self.logger.setLevel(logging.INFO)

            # Also redirect root logger to stderr
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            root_logger.addHandler(stderr_handler)
            root_logger.setLevel(logging.INFO)

        try:
            if transport == "stdio":
                self.run(transport="stdio", **kwargs)
            elif transport == "http":
                self.run(transport="streamable-http", host=host, port=port, **kwargs)
            elif transport == "sse":
                self.run(transport="sse", host=host, port=port, **kwargs)
            else:
                raise ValueError(f"Unsupported transport: {transport}")

        except KeyboardInterrupt:
            self.logger.info("\n🛑 Server stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Server error: {e}")
        finally:
            # Cleanup
            asyncio.run(self.close())

    def _create_mcp_tool_from_tooluniverse(self, tool_config: Dict[str, Any]):
        """Create an MCP tool from a ToolUniverse tool configuration.

        This method creates a function with proper parameter signatures that match
        the ToolUniverse tool schema, enabling FastMCP's automatic parameter validation.
        """
        try:
            # Debug: Ensure tool_config is a dictionary
            if not isinstance(tool_config, dict):
                raise ValueError(
                    f"tool_config must be a dictionary, got {type(tool_config)}: {tool_config}"
                )

            tool_name = tool_config["name"]
            description = tool_config.get(
                "description", f"ToolUniverse tool: {tool_name}"
            )
            parameters = tool_config.get("parameter", {})

            # Extract parameter information from the schema
            # Handle case where properties might be None (like in Finish tool)
            properties = parameters.get("properties")
            if properties is None:
                properties = {}
            required_params = parameters.get("required", [])

            # Handle non-standard schema format where 'required' is set on individual properties
            # instead of at the object level (common in ToolUniverse schemas)
            if not required_params and properties:
                required_params = [
                    param_name
                    for param_name, param_info in properties.items()
                    if param_info.get("required", False)
                ]

            # Build function signature dynamically with Pydantic Field support
            import inspect
            from typing import Annotated
            from pydantic import Field

            # Create parameter signature for the function
            func_params = []
            param_annotations = {}

            # Process parameters in two phases: required first, then optional
            # This ensures Python function signature validity (no default args before non-default)
            for is_required_phase in [True, False]:
                for param_name, param_info in properties.items():
                    param_type = param_info.get("type", "string")
                    param_description = param_info.get(
                        "description", f"{param_name} parameter"
                    )
                    is_required = param_name in required_params

                    # Skip if not in current phase
                    if is_required != is_required_phase:
                        continue

                    # Map JSON schema types to Python types and create appropriate Field
                    field_kwargs = {"description": param_description}

                    if param_type == "string":
                        python_type = str
                        # For string type, don't add json_schema_extra - let Pydantic handle it
                    elif param_type == "integer":
                        python_type = int
                        # For integer type, don't add json_schema_extra - let Pydantic handle it
                    elif param_type == "number":
                        python_type = float
                        # For number type, don't add json_schema_extra - let Pydantic handle it
                    elif param_type == "boolean":
                        python_type = bool
                        # For boolean type, don't add json_schema_extra - let Pydantic handle it
                    elif param_type == "array":
                        python_type = list
                        # Add array-specific schema information only for complex cases
                        items_info = param_info.get("items", {})
                        if items_info:
                            # Clean up items definition - remove invalid fields
                            cleaned_items = items_info.copy()

                            # Remove 'required' field from items (not valid in JSON Schema for array items)
                            if "required" in cleaned_items:
                                cleaned_items.pop("required")

                            field_kwargs["json_schema_extra"] = {
                                "type": "array",
                                "items": cleaned_items,
                            }
                        else:
                            # If no items specified, default to string items
                            field_kwargs["json_schema_extra"] = {
                                "type": "array",
                                "items": {"type": "string"},
                            }
                    elif param_type == "object":
                        python_type = dict
                        # Add object-specific schema information
                        object_props = param_info.get("properties", {})
                        if object_props:
                            # Clean up the nested object properties - fix common schema issues
                            cleaned_props = {}
                            nested_required = []

                            for prop_name, prop_info in object_props.items():
                                cleaned_prop = prop_info.copy()

                                # Fix string "True"/"False" in required field (common ToolUniverse issue)
                                if "required" in cleaned_prop:
                                    req_value = cleaned_prop.pop("required")
                                    if req_value in ["True", "true", True]:
                                        nested_required.append(prop_name)
                                    # Remove the individual required field as it should be at object level

                                cleaned_props[prop_name] = cleaned_prop

                            # Create proper JSON schema for nested object
                            object_schema = {
                                "type": "object",
                                "properties": cleaned_props,
                            }

                            # Add required array at object level if there are required fields
                            if nested_required:
                                object_schema["required"] = nested_required

                            field_kwargs["json_schema_extra"] = object_schema
                    else:
                        # For unknown types, default to string and only add type info if it's truly unknown
                        python_type = str
                        if param_type not in [
                            "string",
                            "integer",
                            "number",
                            "boolean",
                            "array",
                            "object",
                        ]:
                            field_kwargs["json_schema_extra"] = {"type": param_type}

                    # Create Pydantic Field with enhanced schema information
                    pydantic_field = Field(**field_kwargs)

                    if is_required:
                        # Required parameter with description and schema info
                        annotated_type = Annotated[python_type, pydantic_field]
                        param_annotations[param_name] = annotated_type
                        func_params.append(
                            inspect.Parameter(
                                param_name,
                                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                annotation=annotated_type,
                            )
                        )
                    else:
                        # Optional parameter with description, schema info and default value
                        annotated_type = Annotated[
                            Union[python_type, type(None)], pydantic_field
                        ]
                        param_annotations[param_name] = annotated_type
                        func_params.append(
                            inspect.Parameter(
                                param_name,
                                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                default=None,
                                annotation=annotated_type,
                            )
                        )

            # Add optional streaming parameter to signature
            stream_field = Field(
                description="Set to true to receive incremental streaming output (experimental)."
            )
            stream_annotation = Annotated[Union[bool, type(None)], stream_field]
            param_annotations["_tooluniverse_stream"] = stream_annotation
            func_params.append(
                inspect.Parameter(
                    "_tooluniverse_stream",
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=None,
                    annotation=stream_annotation,
                )
            )

            # Note: ctx parameter removed as it causes Pydantic schema issues
            # FastMCP context injection is handled internally by FastMCP

            async def dynamic_tool_function(**kwargs) -> str:
                """Execute ToolUniverse tool with provided arguments."""
                try:
                    # Remove ctx if present (legacy support)
                    ctx = kwargs.pop("ctx", None) if "ctx" in kwargs else None
                    stream_flag = bool(kwargs.get("_tooluniverse_stream"))

                    # Filter out None values for optional parameters (preserve streaming flag)
                    args_dict = {k: v for k, v in kwargs.items() if v is not None}

                    # Validate required parameters (check against args_dict, not filtered_args)
                    missing_required = [
                        param for param in required_params if param not in args_dict
                    ]
                    if missing_required:
                        return json.dumps(
                            {
                                "error": f"Missing required parameters: {missing_required}",
                                "required": required_params,
                                "provided": list(args_dict.keys()),
                            },
                            indent=2,
                        )

                    function_call = {"name": tool_name, "arguments": args_dict}

                    loop = asyncio.get_event_loop()

                    # Initialize stream_callback to None by default
                    stream_callback = None

                    if stream_flag and ctx is not None:

                        def _stream_callback(chunk: str) -> None:
                            if not chunk:
                                return
                            try:
                                future = asyncio.run_coroutine_threadsafe(
                                    ctx.info(chunk), loop
                                )

                                def _log_future_result(fut) -> None:
                                    exc = fut.exception()
                                    if exc:
                                        self.logger.debug(
                                            f"Streaming callback error for {tool_name}: {exc}"
                                        )

                                future.add_done_callback(_log_future_result)
                            except Exception as cb_error:  # noqa: BLE001
                                self.logger.debug(
                                    f"Failed to dispatch stream chunk for {tool_name}: {cb_error}"
                                )

                        # Assign the function to stream_callback
                        stream_callback = _stream_callback

                        # Ensure downstream tools see the streaming flag
                        if "_tooluniverse_stream" not in args_dict:
                            args_dict["_tooluniverse_stream"] = True

                    run_callable = functools.partial(
                        self.tooluniverse.run_one_function,
                        function_call,
                        stream_callback=stream_callback,
                    )

                    result = await loop.run_in_executor(self.executor, run_callable)

                    if isinstance(result, str):
                        return result
                    else:
                        return json.dumps(result, indent=2, default=str)

                except Exception as e:
                    error_msg = f"Error executing {tool_name}: {str(e)}"
                    self.logger.error(error_msg)
                    return json.dumps({"error": error_msg}, indent=2)

            # Set function metadata
            dynamic_tool_function.__name__ = tool_name
            dynamic_tool_function.__signature__ = inspect.Signature(func_params)
            annotations = param_annotations.copy()
            annotations["return"] = str
            dynamic_tool_function.__annotations__ = annotations

            # Create detailed docstring for internal use, but use clean description for FastMCP
            param_docs = []
            for param_name, param_info in properties.items():
                param_desc = param_info.get("description", f"{param_name} parameter")
                param_type = param_info.get("type", "string")
                is_required = param_name in required_params
                required_text = "required" if is_required else "optional"
                param_docs.append(
                    f"    {param_name} ({param_type}, {required_text}): {param_desc}"
                )

            # Set a simple docstring for the function (internal use)
            dynamic_tool_function.__doc__ = f"""{description}

Returns:
    str: Tool execution result
"""

            # Register with FastMCP using explicit description (clean, without parameter list)
            self.tool(description=description)(dynamic_tool_function)

        except Exception as e:
            self.logger.error(f"Error creating MCP tool from config: {e}")
            self.logger.error(f"Error type: {type(e)}")
            import traceback

            self.logger.error(f"Traceback: {traceback.format_exc()}")
            self.logger.debug(f"Tool config: {tool_config}")
            # Don't raise - continue with other tools
            return


# Convenience function for quick server creation
def create_smcp_server(
    name: str = "SMCP Server",
    tool_categories: Optional[List[str]] = None,
    search_enabled: bool = True,
    **kwargs,
) -> SMCP:
    """
    Create a configured SMCP server with common defaults and best practices.

    This convenience function simplifies SMCP server creation by providing
    sensible defaults for common use cases while still allowing full customization
    through additional parameters.

    Parameters:
    ===========
    name : str, default "SMCP Server"
        Human-readable server name used in logs and server identification.
        Choose descriptive names like:
        - "Scientific Research API"
        - "Drug Discovery Server"
        - "Proteomics Analysis Service"

    tool_categories : list of str, optional
        Specific ToolUniverse categories to load. If None, loads all available
        tools (350+ tools). Common category combinations:

        Scientific Research:
        ["ChEMBL", "uniprot", "opentarget", "pubchem", "hpa"]

        Drug Discovery:
        ["ChEMBL", "fda_drug_label", "clinical_trials", "pubchem"]

        Literature Analysis:
        ["EuropePMC", "semantic_scholar", "pubtator", "agents"]

        Minimal Setup:
        ["tool_finder_llm", "special_tools"]

    search_enabled : bool, default True
        Enable AI-powered tool discovery via tools/find method.
        Recommended to keep enabled unless you have specific performance
        requirements or want to minimize dependencies.

    **kwargs**
        Additional SMCP configuration options:

        - tooluniverse_config: Pre-configured ToolUniverse instance
        - auto_expose_tools (bool, default True): Auto-expose ToolUniverse tools
        - max_workers (int, default 5): Thread pool size for tool execution
        - Any FastMCP server options (debug, logging, etc.)

    Returns:
    ========
    SMCP
        Fully configured SMCP server instance ready to run.

    Usage Examples:
    ==============

    Quick Start (all tools):
    ```python
    server = create_smcp_server("Research Server")
    server.run_simple()
    ```

    Focused Server (specific domains):
    ```python
    server = create_smcp_server(
        name="Drug Discovery API",
        tool_categories=["ChEMBL", "fda_drug_label", "clinical_trials"],
        max_workers=10
    )
    server.run_simple(port=8000)
    ```

    Custom Configuration:
    ```python
    server = create_smcp_server(
        name="High-Performance Server",
        search_enabled=True,
        max_workers=20,
        debug=True
    )
    server.run_simple(transport="http", host="0.0.0.0", port=7000)
    ```

    Pre-configured ToolUniverse:
    ```python
    tu = ToolUniverse()
    tu.load_tools(tool_type=["uniprot", "ChEMBL"])
    server = create_smcp_server(
        name="Protein-Drug Server",
        tooluniverse_config=tu,
        search_enabled=True
    )
    ```

    Benefits of Using This Function:
    ===============================

    - **Simplified Setup**: Reduces boilerplate code for common configurations
    - **Best Practices**: Applies recommended settings automatically
    - **Consistent Naming**: Encourages good server naming conventions
    - **Future-Proof**: Will include new recommended defaults in future versions
    - **Documentation**: Provides clear examples and guidance

    Equivalent Manual Configuration:
    ===============================
    This function is equivalent to:
    ```python
    server = SMCP(
        name=name,
        tool_categories=tool_categories,
        search_enabled=search_enabled,
        auto_expose_tools=True,
        max_workers=5,
        **kwargs
    )
    ```

    When to Use Manual Configuration:
    ================================
    - Need precise control over all initialization parameters
    - Using custom ToolUniverse configurations
    - Implementing custom MCP methods or tools
    - Advanced deployment scenarios with specific requirements
    """
    return SMCP(
        name=name,
        tool_categories=tool_categories,
        search_enabled=search_enabled,
        **kwargs,
    )
