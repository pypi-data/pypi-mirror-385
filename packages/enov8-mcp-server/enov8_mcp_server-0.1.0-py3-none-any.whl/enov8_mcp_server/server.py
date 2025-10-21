from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("enov8-ecosystem")

# Constants - Load from environment variables
ENOV8_API_BASE = os.getenv("ENOV8_API_BASE")
ENOV8_USER_ID = os.getenv("ENOV8_USER_ID")
ENOV8_APP_ID = os.getenv("ENOV8_APP_ID")
ENOV8_APP_KEY = os.getenv("ENOV8_APP_KEY")

# Validate required environment variables
if not all([ENOV8_API_BASE, ENOV8_USER_ID, ENOV8_APP_ID, ENOV8_APP_KEY]):
    raise ValueError(
        "Missing required environment variables. Please set:\n"
        "- ENOV8_API_BASE (e.g., https://dashboard.enov8.com/ecosystem/api)\n"
        "- ENOV8_USER_ID\n"
        "- ENOV8_APP_ID\n"
        "- ENOV8_APP_KEY"
    )


async def make_enov8_request(endpoint: str) -> dict[str, Any] | list[dict[str, Any]] | None:
    """Make a request to the Enov8 API with proper error handling."""
    url = f"{ENOV8_API_BASE}/{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "user-id": ENOV8_USER_ID,
        "app-id": ENOV8_APP_ID,
        "app-key": ENOV8_APP_KEY
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except httpx.TimeoutException:
            return {"error": "Request timeout - API took too long to respond"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}


def filter_items(items: list[dict], search_query: str, search_fields: list[str]) -> list[dict]:
    """Filter items based on search query across multiple fields."""
    if not search_query:
        return items
    
    search_lower = search_query.lower()
    filtered = []
    
    for item in items:
        for field in search_fields:
            value = item.get(field) or ""
            if search_lower in str(value).lower():
                filtered.append(item)
                break
    
    return filtered


# ==================== TOOL 1: GET SYSTEMS ====================

@mcp.tool()
async def get_systems(search_query: str = "") -> str:
    """Get systems from the Enov8 ecosystem.
    
    Use this when user asks about systems, infrastructure, applications, or ecosystem components.
    
    Args:
        search_query: Optional search term to filter by system name, Resource ID, or Type
    """
    data = await make_enov8_request("System")
    
    if not data or isinstance(data, dict) and "error" in data:
        return f"❌ Error fetching systems: {data.get('error', 'Unknown error')}"
    
    systems = data if isinstance(data, list) else []
    
    if not systems:
        return "No systems found in the ecosystem."
    
    # Filter if search query provided
    if search_query:
        systems = filter_items(systems, search_query, [
            "Resource Name", "Resource ID", "System ID", "Type", "Business Unit", "Description"
        ])
        
        if not systems:
            return f"No systems found matching '{search_query}'."
    
    # Format response
    result = f"Found {len(systems)} system{'s' if len(systems) != 1 else ''}"
    if search_query:
        result += f" matching '{search_query}'"
    result += ":\n\n"
    
    for idx, system in enumerate(systems, 1):
        result += f"{idx}. **{system.get('Resource Name', 'N/A')}** ({system.get('Resource ID', 'N/A')})\n"
        result += f"   • Type: {system.get('Type', 'N/A')} | Status: {system.get('Status', 'N/A')}\n"
        result += f"   • Business Unit: {system.get('Business Unit', 'N/A')}\n"
        result += f"   • Description: {system.get('Description', 'N/A')}\n"
        
        if system.get('Dependencies'):
            result += f"   • Dependencies: {system.get('Dependencies')}\n"
        
        result += "\n"
    
    return result


# ==================== TOOL 2: GET PROJECTS ====================

@mcp.tool()
async def get_projects(search_query: str = "") -> str:
    """Get projects from the Enov8 ecosystem.
    
    Use this when user asks about projects, releases, initiatives, or project status.
    
    Args:
        search_query: Optional search term to filter by project name, alias, or status
    """
    data = await make_enov8_request("Project")
    
    if not data or isinstance(data, dict) and "error" in data:
        return f"❌ Error fetching projects: {data.get('error', 'Unknown error')}"
    
    projects = data if isinstance(data, list) else []
    
    if not projects:
        return "No projects found in the ecosystem."
    
    # Filter if search query provided
    if search_query:
        projects = filter_items(projects, search_query, [
            "Project Name", "Project Alias", "Project Status", "Program Name", "System"
        ])
        
        if not projects:
            return f"No projects found matching '{search_query}'."
    
    # Format response
    result = f"Found {len(projects)} project{'s' if len(projects) != 1 else ''}"
    if search_query:
        result += f" matching '{search_query}'"
    result += ":\n\n"
    
    for idx, project in enumerate(projects, 1):
        result += f"{idx}. **{project.get('Project Name', 'N/A')}** ({project.get('Project Alias', 'N/A')})\n"
        result += f"   • Program: {project.get('Program Name', 'N/A')}\n"
        result += f"   • Status: {project.get('Project Status', 'N/A')} | Phase: {project.get('Project Phase', 'N/A')}\n"
        result += f"   • RAG: {project.get('RAG Status', 'N/A')} | Completed: {project.get('Percentage Completed', '0')}%\n"
        result += f"   • Business Unit: {project.get('Business Unit', 'N/A')}\n"
        result += f"   • Timeline: {project.get('Start Date', 'N/A')} to {project.get('End Date', 'N/A')}\n"
        
        if project.get('System'):
            result += f"   • Systems: {project.get('System')}\n"
        
        result += "\n"
    
    return result


# ==================== TOOL 3: GET SERVICE REQUESTS ====================

@mcp.tool()
async def get_service_requests(search_query: str = "") -> str:
    """Get service requests from the Enov8 ecosystem.
    
    Use this when user asks about tickets, service requests, incidents, or support issues.
    
    Args:
        search_query: Optional search term to filter by summary, status, or priority
    """
    data = await make_enov8_request("ServiceRequest")
    
    if not data or isinstance(data, dict) and "error" in data:
        return f"❌ Error fetching service requests: {data.get('error', 'Unknown error')}"
    
    requests_list = data if isinstance(data, list) else []
    
    if not requests_list:
        return "No service requests found in the ecosystem."
    
    # Filter if search query provided
    if search_query:
        requests_list = filter_items(requests_list, search_query, [
            "Summary", "Status", "Priority", "Type", "Assigned To"
        ])
        
        if not requests_list:
            return f"No service requests found matching '{search_query}'."
    
    # Format response
    result = f"Found {len(requests_list)} service request{'s' if len(requests_list) != 1 else ''}"
    if search_query:
        result += f" matching '{search_query}'"
    result += ":\n\n"
    
    for idx, req in enumerate(requests_list, 1):
        result += f"{idx}. **{req.get('Summary', 'N/A')}**\n"
        result += f"   • ID: {req.get('System ID', 'N/A')}\n"
        result += f"   • Type: {req.get('Type', 'N/A')} | Status: {req.get('Status', 'N/A')}\n"
        result += f"   • Priority: {req.get('Priority', 'N/A')}\n"
        result += f"   • Assigned To: {req.get('Assigned To', 'N/A')}\n"
        
        if req.get('Project'):
            result += f"   • Project: {req.get('Project')}\n"
        
        result += "\n"
    
    return result


# ==================== TOOL 4: GET EVENTS ====================

@mcp.tool()
async def get_events(search_query: str = "") -> str:
    """Get environment events from the Enov8 ecosystem.
    
    Use this when user asks about events, incidents, environment changes, or deployments.
    
    Args:
        search_query: Optional search term to filter by event summary or type
    """
    data = await make_enov8_request("Event")
    
    if not data or isinstance(data, dict) and "error" in data:
        return f"❌ Error fetching events: {data.get('error', 'Unknown error')}"
    
    events = data if isinstance(data, list) else []
    
    if not events:
        return "No events found in the ecosystem."
    
    # Filter if search query provided
    if search_query:
        events = filter_items(events, search_query, [
            "Summary", "Type", "Status", "Environment", "Project"
        ])
        
        if not events:
            return f"No events found matching '{search_query}'."
    
    # Format response
    result = f"Found {len(events)} event{'s' if len(events) != 1 else ''}"
    if search_query:
        result += f" matching '{search_query}'"
    result += ":\n\n"
    
    for idx, event in enumerate(events, 1):
        result += f"{idx}. **{event.get('Summary', 'N/A')}**\n"
        result += f"   • Type: {event.get('Type', 'N/A')} | Status: {event.get('Status', 'N/A')}\n"
        result += f"   • Environment: {event.get('Environment', 'N/A')}\n"
        result += f"   • Start: {event.get('Start Timestamp', 'N/A')}\n"
        result += f"   • End: {event.get('End Timestamp', 'N/A')}\n"
        
        if event.get('Project'):
            result += f"   • Project: {event.get('Project')}\n"
        
        result += "\n"
    
    return result


# ==================== TOOL 5: GET BOOKINGS ====================

@mcp.tool()
async def get_bookings(search_query: str = "") -> str:
    """Get environment bookings from the Enov8 ecosystem.
    
    Use this when user asks about bookings, reservations, or environment allocations.
    
    Args:
        search_query: Optional search term to filter by project, environment, or status
    """
    data = await make_enov8_request("Booking")
    
    if not data or isinstance(data, dict) and "error" in data:
        return f"❌ Error fetching bookings: {data.get('error', 'Unknown error')}"
    
    bookings = data if isinstance(data, list) else []
    
    if not bookings:
        return "No bookings found in the ecosystem."
    
    # Filter if search query provided
    if search_query:
        bookings = filter_items(bookings, search_query, [
            "Summary", "Project", "Environment", "Status", "SubType"
        ])
        
        if not bookings:
            return f"No bookings found matching '{search_query}'."
    
    # Format response
    result = f"Found {len(bookings)} booking{'s' if len(bookings) != 1 else ''}"
    if search_query:
        result += f" matching '{search_query}'"
    result += ":\n\n"
    
    for idx, booking in enumerate(bookings, 1):
        result += f"{idx}. **{booking.get('Summary', 'N/A')}**\n"
        result += f"   • Project: {booking.get('Project', 'N/A')}\n"
        result += f"   • Environment: {booking.get('Environment', 'N/A')}\n"
        result += f"   • Type: {booking.get('SubType', 'N/A')} | Status: {booking.get('Status', 'N/A')}\n"
        result += f"   • Start: {booking.get('Start Timestamp', 'N/A')}\n"
        result += f"   • End: {booking.get('End Timestamp', 'N/A')}\n"
        result += f"   • Assigned To: {booking.get('Assigned To', 'N/A')}\n"
        result += "\n"
    
    return result


# ==================== TOOL 6: GET ENVIRONMENTS ====================

@mcp.tool()
async def get_environments(search_query: str = "") -> str:
    """Get environments from the Enov8 ecosystem.
    
    Use this when user asks about environments, environment types, or environment status.
    
    Args:
        search_query: Optional search term to filter by environment name or type
    """
    data = await make_enov8_request("Environment")
    
    if not data or isinstance(data, dict) and "error" in data:
        return f"❌ Error fetching environments: {data.get('error', 'Unknown error')}"
    
    environments = data if isinstance(data, list) else []
    
    if not environments:
        return "No environments found in the ecosystem."
    
    # Filter if search query provided
    if search_query:
        environments = filter_items(environments, search_query, [
            "Environment Name", "Type", "Status", "Purpose"
        ])
        
        if not environments:
            return f"No environments found matching '{search_query}'."
    
    # Format response
    result = f"Found {len(environments)} environment{'s' if len(environments) != 1 else ''}"
    if search_query:
        result += f" matching '{search_query}'"
    result += ":\n\n"
    
    for idx, env in enumerate(environments, 1):
        result += f"{idx}. **{env.get('Environment Name', 'N/A')}**\n"
        result += f"   • Type: {env.get('Type', 'N/A')} | Status: {env.get('Status', 'N/A')}\n"
        result += f"   • Purpose: {env.get('Purpose', 'N/A')}\n"
        
        if env.get('SystemInstance'):
            result += f"   • Instances: {env.get('SystemInstance')}\n"
        
        result += "\n"
    
    return result


# ==================== TOOL 7: GET SYSTEM INSTANCES ====================

@mcp.tool()
async def get_system_instances(search_query: str = "") -> str:
    """Get system instances from the Enov8 ecosystem.
    
    Use this when user asks about instances, deployments, or environment-specific systems.
    
    Args:
        search_query: Optional search term to filter by instance name, system, or environment
    """
    data = await make_enov8_request("SystemInstance")
    
    if not data or isinstance(data, dict) and "error" in data:
        return f"❌ Error fetching system instances: {data.get('error', 'Unknown error')}"
    
    instances = data if isinstance(data, list) else []
    
    if not instances:
        return "No system instances found in the ecosystem."
    
    # Filter if search query provided
    if search_query:
        instances = filter_items(instances, search_query, [
            "Instance Name", "System", "Environment", "Status", "Type"
        ])
        
        if not instances:
            return f"No system instances found matching '{search_query}'."
    
    # Format response
    result = f"Found {len(instances)} system instance{'s' if len(instances) != 1 else ''}"
    if search_query:
        result += f" matching '{search_query}'"
    result += ":\n\n"
    
    for idx, instance in enumerate(instances, 1):
        result += f"{idx}. **{instance.get('Instance Name', 'N/A')}**\n"
        result += f"   • System: {instance.get('System', 'N/A')}\n"
        result += f"   • Environment: {instance.get('Environment', 'N/A')}\n"
        result += f"   • Status: {instance.get('Status', 'N/A')}\n"
        
        if instance.get('Version'):
            result += f"   • Version: {instance.get('Version')}\n"
        
        result += "\n"
    
    return result


# ==================== TOOL 8: GET SYSTEM COMPONENTS ====================

@mcp.tool()
async def get_system_components(search_query: str = "") -> str:
    """Get system components from the Enov8 ecosystem.
    
    Use this when user asks about components, modules, or system parts.
    
    Args:
        search_query: Optional search term to filter by component name or system
    """
    data = await make_enov8_request("SystemComponent")
    
    if not data or isinstance(data, dict) and "error" in data:
        return f"❌ Error fetching system components: {data.get('error', 'Unknown error')}"
    
    components = data if isinstance(data, list) else []
    
    if not components:
        return "No system components found in the ecosystem."
    
    # Filter if search query provided
    if search_query:
        components = filter_items(components, search_query, [
            "Component Name", "System", "Type", "Status"
        ])
        
        if not components:
            return f"No system components found matching '{search_query}'."
    
    # Format response
    result = f"Found {len(components)} system component{'s' if len(components) != 1 else ''}"
    if search_query:
        result += f" matching '{search_query}'"
    result += ":\n\n"
    
    for idx, component in enumerate(components, 1):
        result += f"{idx}. **{component.get('Component Name', 'N/A')}**\n"
        result += f"   • System: {component.get('System', 'N/A')}\n"
        result += f"   • Type: {component.get('Type', 'N/A')}\n"
        result += f"   • Status: {component.get('Status', 'N/A')}\n"
        result += "\n"
    
    return result


# ==================== TOOL 9: GET RELEASES ====================

@mcp.tool()
async def get_releases(search_query: str = "") -> str:
    """Get releases from the Enov8 ecosystem.
    
    Use this when user asks about releases, release schedules, or go-live dates.
    
    Args:
        search_query: Optional search term to filter by release name or status
    """
    data = await make_enov8_request("Release")
    
    if not data or isinstance(data, dict) and "error" in data:
        return f"❌ Error fetching releases: {data.get('error', 'Unknown error')}"
    
    releases = data if isinstance(data, list) else []
    
    if not releases:
        return "No releases found in the ecosystem."
    
    # Filter if search query provided
    if search_query:
        releases = filter_items(releases, search_query, [
            "Release", "Summary", "Release Status", "Release Type", "Project"
        ])
        
        if not releases:
            return f"No releases found matching '{search_query}'."
    
    # Format response
    result = f"Found {len(releases)} release{'s' if len(releases) != 1 else ''}"
    if search_query:
        result += f" matching '{search_query}'"
    result += ":\n\n"
    
    for idx, release in enumerate(releases, 1):
        result += f"{idx}. **{release.get('Release', 'N/A')}** - {release.get('Summary', 'N/A')}\n"
        result += f"   • Type: {release.get('Release Type', 'N/A')}\n"
        result += f"   • Status: {release.get('Release Status', 'N/A')} | RAG: {release.get('RAG Status', 'N/A')}\n"
        result += f"   • Completed: {release.get('Percentage Completed', '0')}%\n"
        result += f"   • Timeline: {release.get('Start Date', 'N/A')} to {release.get('End Date', 'N/A')}\n"
        result += f"   • Go Live: {release.get('Go Live Date', 'N/A')}\n"
        
        if release.get('Project'):
            result += f"   • Projects: {release.get('Project')}\n"
        
        result += "\n"
    
    return result


# ==================== OPTIONAL: RESOURCES ====================

@mcp.resource("enov8://system/{system_id}")
async def get_system_resource(system_id: str) -> str:
    """Get detailed information about a specific system by ID."""
    data = await make_enov8_request("System")
    
    if not data or isinstance(data, dict) and "error" in data:
        return f"Error: {data.get('error', 'Unknown error')}"
    
    systems = data if isinstance(data, list) else []
    
    # Find system by ID
    for system in systems:
        if system.get('System ID') == system_id or system.get('Resource ID') == system_id:
            result = f"# {system.get('Resource Name', 'N/A')}\n\n"
            result += f"**ID:** {system.get('System ID', 'N/A')}\n"
            result += f"**Resource ID:** {system.get('Resource ID', 'N/A')}\n"
            result += f"**Type:** {system.get('Type', 'N/A')}\n"
            result += f"**Status:** {system.get('Status', 'N/A')}\n"
            result += f"**Business Unit:** {system.get('Business Unit', 'N/A')}\n\n"
            result += f"**Description:**\n{system.get('Description', 'N/A')}\n\n"
            
            if system.get('Dependencies'):
                result += f"**Dependencies:** {system.get('Dependencies')}\n\n"
            
            if system.get('SystemInstance'):
                result += f"**Instances:** {system.get('SystemInstance')}\n\n"
            
            return result
    
    return f"System with ID '{system_id}' not found."


@mcp.resource("enov8://info")
def get_info_resource() -> str:
    """Get information about the Enov8 MCP server and available tools."""
    return """
# Enov8 Ecosystem MCP Server v2 (No Limits)

This server provides access to the Enov8 ecosystem management platform.

## Available Tools:

1. **get_systems** - Query systems and infrastructure
2. **get_projects** - Query projects and initiatives
3. **get_service_requests** - Query service requests and tickets
4. **get_events** - Query environment events
5. **get_bookings** - Query environment bookings
6. **get_environments** - Query environments
7. **get_system_instances** - Query system instances
8. **get_system_components** - Query system components
9. **get_releases** - Query releases

## Usage Examples:

- "List all systems in production"
- "Show me projects with status 'In Progress'"
- "What service requests are assigned to me?"
- "Show upcoming environment bookings"
- "What releases are scheduled this month?"
- "How many total systems are there?"

## Features:

- **No result limits** - Returns ALL matching data
- Search and filtering across all resources
- Formatted, human-readable responses
- Async API calls for better performance
- Proper error handling and validation

## Configuration:

Set these environment variables (all required):
- ENOV8_API_BASE (e.g., https://dashboard.enov8.com/ecosystem/api)
- ENOV8_USER_ID (your user ID)
- ENOV8_APP_ID (your application ID)
- ENOV8_APP_KEY (your application key)

## Notes:

⚠️ This version returns ALL results without limits. Use with large context models (Claude Sonnet, GPT-4, etc.)
If you experience token overflow errors, use the original version with limits instead.
"""

