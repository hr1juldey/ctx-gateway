# ctx-gateway — design notes

## The problem, measured
N MCP servers ≈ N × (tool definitions + schemas) injected into the agent's context before the first user token. Published reports: 3 servers ≈ 55k tokens (roadie.io). At ~100 servers (a real mid-size org) this is not degradation, it is failure — cost and stability both.

## The three claims to prove (benchmark = the product)
1. **Context cost**: tool-def tokens per request, naive vs gateway (target: order-of-magnitude).
2. **Task success**: multi-tool tasks succeed at equal-or-better rate with the subgraph.
3. **Stability**: kill any upstream mid-run; workflow survives (isolation gate).

## Architecture (v0)
- `registry` — upstream MCP servers; capability index (name, description, schema digest, embeddings optional).
- `router` — per-task tool subgraph selection (v0: lexical/embedding retrieval over the capability index; v1: tuned small model).
- `budget` — hard cap on tool-def tokens; router must fit under it.
- `executor` — chain orchestration across upstreams; retries, circuit breaker per upstream.
- Transport: MCP server (stdio + websocket) speaking to any MCP client.

## v0 language: Python (official `mcp` SDK) — port-to-Go is roadmap, not day 1.
