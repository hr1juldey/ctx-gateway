"""Demo upstream MCP server: a tiny notes/filesystem stand-in.

Realistic tool shapes (list + keyed read) so the gateway's federation
and schema passthrough are exercised honestly. Part of the Day-1 demo
fleet; the fleet generator (Day 3) will supersede these.
"""
from mcp.server.mcpserver import MCPServer

server = MCPServer(
    name="files",
    version="0.1.0",
    description="Demo upstream: in-memory notes store",
)

NOTES = {
    "readme": "ctx-gateway demo upstream. The gateway federates this server over stdio.",
    "metrics": "placeholder: benchmark metrics land here on Day 10.",
}


@server.tool()
def list_notes() -> list[str]:
    """List the names of all available notes."""
    return sorted(NOTES.keys())


@server.tool()
def read_note(name: str) -> str:
    """Read the full text of a note by its exact name.

    Args:
        name: Exact note name, as returned by list_notes.
    """
    note = NOTES.get(name)
    if note is None:
        return f"error: no note named {name!r}. Valid: {sorted(NOTES.keys())}"
    return note


if __name__ == "__main__":
    server.run()
