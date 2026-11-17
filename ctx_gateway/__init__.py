"""ctx-gateway: federate many MCP servers behind one stable endpoint.

The gateway holds live client sessions to every configured upstream MCP
server and republishes their tools under collision-safe prefixed names
(``{upstream}__{tool}``), preserving each tool's input schema. A client
talks only to the gateway; the gateway routes calls to the owning
upstream and returns the result.

Day-1 scope (v0.1 Federate): registry, upstream sessions, aggregate
list, prefixed routing, one round-trip test. Routing/budgets (v0.2),
failure isolation (v0.3) come later per ROADMAP.
"""
from ctx_gateway.gateway import Gateway

__all__ = ["Gateway"]
__version__ = "0.1.0"
