"""Federation core: hold upstream MCP sessions, aggregate, route."""
from __future__ import annotations


from mcp import types as mt
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

PREFIX_SEP = "__"


def prefixed_name(upstream: str, tool: str) -> str:
    return f"{upstream}{PREFIX_SEP}{tool}"


def split_prefixed(name: str) -> tuple[str, str]:
    upstream, _, tool = name.partition(PREFIX_SEP)
    return upstream, tool


class Upstream:
    """One live stdio connection to an upstream MCP server."""

    def __init__(self, name: str, command: str, args: list[str]):
        self.name = name
        self.command = command
        self.args = args
        self._cm = None
        self.session: ClientSession | None = None

    async def connect(self):
        params = StdioServerParameters(command=self.command, args=self.args)
        self._cm = stdio_client(params)
        read, write = await self._cm.__aenter__()
        self.session = ClientSession(read, write)
        await self.session.__aenter__()
        await self.session.initialize()
        return self

    async def close(self):
        if self.session is not None:
            await self.session.__aexit__(None, None, None)
            self.session = None
        if self._cm is not None:
            await self._cm.__aexit__(None, None, None)
            self._cm = None


class Gateway:
    """Aggregates tools from all upstreams under prefixed names."""

    def __init__(self, upstreams: list[Upstream]):
        self.upstreams = {u.name: u for u in upstreams}
        self._tools: dict[str, mt.Tool] = {}  # prefixed name -> upstream Tool

    async def connect(self) -> "Gateway":
        # NOTE: stdio_client cancel scopes must be entered AND exited in
        # the same task (anyio constraint), so upstreams connect/close
        # sequentially in the owning task — never via start_soon.
        for u in self.upstreams.values():
            await u.connect()
        await self.refresh_tools()
        return self

    async def close(self) -> None:
        for u in self.upstreams.values():
            await u.close()

    async def refresh_tools(self) -> int:
        self._tools = {}
        for name, u in self.upstreams.items():
            if u.session is None:
                continue
            result = await u.session.list_tools()
            for tool in result.tools:
                self._tools[prefixed_name(name, tool.name)] = tool
        return len(self._tools)

    @property
    def tools(self) -> dict[str, mt.Tool]:
        return dict(self._tools)

    async def call_tool(self, name: str, arguments: dict | None = None) -> list[mt.ContentBlock]:
        """Route a prefixed tool call to its owning upstream."""
        if name not in self._tools:
            raise KeyError(
                f"unknown tool {name!r}; known: {sorted(self._tools)}"
            )
        upstream_name, tool_name = split_prefixed(name)
        upstream = self.upstreams[upstream_name]
        result = await upstream.session.call_tool(tool_name, arguments or {})
        if result.is_error:
            texts = [
                getattr(b, "text", repr(b)) for b in result.content
            ]
            raise RuntimeError(f"upstream error from {upstream_name}: {'; '.join(texts)}")
        return result.content
