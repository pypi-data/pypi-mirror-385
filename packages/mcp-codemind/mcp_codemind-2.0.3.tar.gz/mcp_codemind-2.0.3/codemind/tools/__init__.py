"""Tool registration for FastMCP server."""
from fastmcp import FastMCP

# Import all tool functions
from .search import (
    search_existing_code,
    check_functionality_exists,
    search_by_export,
    get_similar_files
)

from .context import (
    get_file_context,
    query_recent_changes,
    record_decision,
    list_all_decisions
)

from .dependencies import (
    find_dependencies,
    get_import_graph,
    get_call_tree
)

from .analysis import (
    get_code_metrics_summary,
    find_configuration_inconsistencies
)

from .refactoring import (
    check_breaking_changes,
    find_usage_examples,
    get_test_coverage
)

from .management import (
    force_reindex,
    index_file,
    find_todo_and_fixme,
    get_file_history_summary
)


def register_all_tools(mcp: FastMCP):
    """Register all 20 CodeMind tools with the MCP server."""
    
    # Search & Discovery Tools (4)
    mcp.tool()(search_existing_code)
    mcp.tool()(check_functionality_exists)
    mcp.tool()(search_by_export)
    mcp.tool()(get_similar_files)
    
    # Context & History Tools (4)
    mcp.tool()(get_file_context)
    mcp.tool()(query_recent_changes)
    mcp.tool()(record_decision)
    mcp.tool()(list_all_decisions)
    
    # Dependency Analysis Tools (3)
    mcp.tool()(find_dependencies)
    mcp.tool()(get_import_graph)
    mcp.tool()(get_call_tree)
    
    # Code Analysis Tools (2)
    mcp.tool()(get_code_metrics_summary)
    mcp.tool()(find_configuration_inconsistencies)
    
    # Refactoring Safety Tools (3)
    mcp.tool()(check_breaking_changes)
    mcp.tool()(find_usage_examples)
    mcp.tool()(get_test_coverage)
    
    # Index Management Tools (4)
    mcp.tool()(force_reindex)
    mcp.tool()(index_file)
    mcp.tool()(find_todo_and_fixme)
    mcp.tool()(get_file_history_summary)
    
    return mcp
