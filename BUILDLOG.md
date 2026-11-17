# BUILDLOG

Public build log — 14 days, clean-room rebuild of a pattern I shipped in production (org-wide MCP gateway, 93% token-cost cut). One entry per day, with the numbers as they land.

- **Day 0** — scaffold, thesis, benchmark design. (today)
- Day 1..14 — the plan: federation → subgraph routing → token budgets → failure isolation → chain execution → reproducible benchmark → rendered explainer.

Why public: the only evidence that counts is a repo someone can run.

## Day 1 — Federation core (2026-11-17)

**Shipped:** v0.1 Federate. `ctx_gateway/gateway.py` holds live stdio client
sessions to every configured upstream MCP server; `ctx_gateway/server.py`
republishes all tools under `{upstream}__{tool}` names with schema-faithful
dynamic wrappers; `test_roundtrip.py` proves the full chain
client -> gateway -> upstream -> back.

**Verified:** 2 upstreams, 4 aggregated tools, schema passthrough (required
params + optional defaults preserved), routed calls across both upstreams,
upstream error surfacing. `uv run python -m test_roundtrip` -> PASS.

**Bugs found and fixed (the interesting part):**
1. anyio cancel-scope law: stdio_client context managers must be entered AND
   exited in the same task. Connecting upstreams via `tg.start_soon` put each
   CM in its own task; the scope exit later in a different task deadlocked the
   loop. Fix: sequential connect/close in the owning task.
2. mcp 2.x is snake_case (`input_schema`, `is_error`, `server_info`) and
   renamed FastMCP -> MCPServer.
3. The nasty one: mapping JSON-schema `"number"` to the tuple annotation
   `(int, float)` crashes `Tool.from_function` (Annotated[] requires a type,
   not a tuple) — and because the crash happened while building tools inside
   the async main, it surfaced as a *silent hang*, not a traceback. Symptom:
   gateway process alive, never answering `initialize`. Diagnosis trail:
   bare server -> fine; instrumented build_server -> `add_tool` never
   returned; standalone repro with faulthandler -> TypeError at last.
   Fix: `"number" -> float`. Lesson recorded: a sync crash inside async
   setup can masquerade as a protocol hang; instrument before theorizing.
