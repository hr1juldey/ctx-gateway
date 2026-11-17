"""The gateway as an MCP server: prefixed tools with passthrough schemas."""
from __future__ import annotations

import json
import os
import sys
import inspect as _t

from ctx_gateway.gateway import Gateway, Upstream

REGISTRY_DEFAULT = [
    {"name": "calc", "command": sys.executable, "args": ["-m", "upstreams.calc_server"]},
    {"name": "files", "command": sys.executable, "args": ["-m", "upstreams.files_server"]},
]

# JSON schema type -> Python annotation, for schema-faithful wrappers.
# NOTE: single types only — tuple annotations like (int, float) crash
# Tool.from_function (Annotated[] requires a type, not a tuple) and the
# error manifests as a silent stall inside the running event loop.
_TYPE_MAP = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
    "array": list,
    "object": dict,
    "null": type(None),
}


def _blocks_to_text(blocks) -> str:
    from mcp.types import TextContent

    parts = []
    for b in blocks:
        if isinstance(b, TextContent):
            parts.append(b.text)
        else:
            parts.append(json.dumps(getattr(b, "model_dump", lambda: str(b))()))
    return "\n".join(parts) if parts else "ok"


def _build_wrapper(gateway: Gateway, tool_name: str, schema: dict):
    """Async callable whose signature mirrors the upstream tool's input
    schema, so the gateway republishes real schemas, not blobs."""
    properties: dict = (schema or {}).get("properties", {}) or {}
    required = set((schema or {}).get("required", []) or [])

    async def wrapper(**kwargs):
        blocks = await gateway.call_tool(tool_name, kwargs)
        return _blocks_to_text(blocks)

    params = []
    for prop_name, prop in properties.items():
        py_type = _TYPE_MAP.get(prop.get("type", "string"), str)
        if prop_name in required:
            default = _t.Parameter.empty
        else:
            default = prop.get("default")
        params.append(
            _t.Parameter(
                prop_name,
                _t.Parameter.POSITIONAL_OR_KEYWORD,
                default=default,
                annotation=py_type,
            )
        )
    wrapper.__signature__ = _t.Signature(parameters=params)
    wrapper.__annotations__ = {p.name: p.annotation for p in params}
    wrapper.__doc__ = (schema or {}).get("description", "")
    return wrapper


def build_server(gateway: Gateway):
    from mcp.server.mcpserver import MCPServer

    server = MCPServer(
        name="ctx-gateway",
        version="0.1.0",
        description="Federate many MCP servers behind one stable endpoint.",
        instructions=(
            "All tools are namespaced as {upstream}__{tool}. "
            "Call them exactly as listed; schemas mirror the upstream."
        ),
    )
    for prefixed, tool in sorted(gateway.tools.items()):
        upstream = prefixed.partition("__")[0]
        wrapper = _build_wrapper(gateway, prefixed, tool.input_schema)
        server.add_tool(
            wrapper,
            name=prefixed,
            description=(tool.description or "") + f" [via {upstream}]",
        )
    return server


async def main() -> None:
    registry_path = os.environ.get("CTX_GATEWAY_REGISTRY")
    if registry_path and os.path.exists(registry_path):
        registry = json.load(open(registry_path))
    else:
        registry = REGISTRY_DEFAULT

    upstreams = [Upstream(**u) for u in registry]
    gateway = await Gateway(upstreams).connect()
    print(
        f"ctx-gateway: federated {len(upstreams)} upstreams, "
        f"{len(gateway.tools)} tools",
        file=sys.stderr,
    )
    try:
        server = build_server(gateway)
        await server.run_stdio_async()
    finally:
        await gateway.close()


if __name__ == "__main__":
    import anyio

    anyio.run(main)
