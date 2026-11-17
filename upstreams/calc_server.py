"""Demo upstream MCP server: arithmetic tools.

Second member of the Day-1 demo fleet. Distinct tool signatures (typed
numeric params) so schema passthrough is visibly correct downstream.
"""
from mcp.server.mcpserver import MCPServer

server = MCPServer(
    name="calc",
    version="0.1.0",
    description="Demo upstream: arithmetic tools",
)


@server.tool()
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@server.tool()
def multiply(a: float, b: float, *, round_to: int = 2) -> float:
    """Multiply two numbers, optionally rounding the product.

    Args:
        a: First factor.
        b: Second factor.
        round_to: Decimal places to round to (default 2).
    """
    product = a * b
    return round(product, round_to)


if __name__ == "__main__":
    server.run()
