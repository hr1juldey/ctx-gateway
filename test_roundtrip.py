"""Day-1 acceptance test: full round trip through the gateway.

client -> gateway (stdio) -> upstream (stdio) -> back.
Verifies: prefixed aggregation, schema passthrough, routed calls.
Run: .venv/bin/python -m test_roundtrip
"""
from __future__ import annotations

import json
import sys

import anyio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.types import TextContent

GATEWAY_CMD = [
    sys.executable,
    "-m",
    "ctx_gateway.server",
]


def text_of(result) -> str:
    parts = [
        b.text if isinstance(b, TextContent) else repr(b) for b in result.content
    ]
    return "\n".join(parts)


async def run_test() -> None:
    params = StdioServerParameters(command=GATEWAY_CMD[0], args=GATEWAY_CMD[1:])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as client:
            await client.initialize()

            result = await client.list_tools()
            tools = result.tools
            print(f"[1] gateway exposes {len(tools)} tools:")
            total_schema_chars = 0
            for t in tools:
                schema = json.dumps(t.input_schema)
                total_schema_chars += len(schema)
                print(
                    f"    - {t.name:22s} schema={len(schema):4d} chars "
                    f"required={[r for r in t.input_schema.get('required', [])]}"
                )
            print(f"    total tool-def payload: {total_schema_chars} chars")

            names = {t.name for t in tools}
            assert "calc__add" in names, names
            assert "files__list_notes" in names, names

            print("\n[2] schema passthrough check (calc__multiply):")
            mul = next(t for t in tools if t.name == "calc__multiply")
            props = mul.input_schema.get("properties", {})
            print(f"    properties: {sorted(props)}")
            assert {"a", "b", "round_to"} <= set(props), props

            print("\n[3] routed calls (client -> gateway -> upstream):")
            r1 = await client.call_tool("calc__add", {"a": 20, "b": 22})
            print(f"    calc__add(20, 22)            -> {text_of(r1)}")
            assert float(text_of(r1).strip()) == 42.0

            r2 = await client.call_tool("files__read_note", {"name": "readme"})
            print(f"    files__read_note('readme')   -> {text_of(r1)[:0]}{text_of(r2)[:60]}...")
            assert "federates this server" in text_of(r2)

            r3 = await client.call_tool("calc__multiply", {"a": 1.5, "b": 4})
            print(f"    calc__multiply(1.5, 4)       -> {text_of(r3)}")
            assert text_of(r3).strip() == "6.0"

            r4 = await client.call_tool("files__list_notes", {})
            print(f"    files__list_notes()          -> {text_of(r4)}")

            print("\n[4] error surface (bad note name):")
            r5 = await client.call_tool("files__read_note", {"name": "nope"})
            print(f"    -> {text_of(r5)[:70]}")

    print("\nPASS: federation round trip verified")


if __name__ == "__main__":
    anyio.run(run_test)
