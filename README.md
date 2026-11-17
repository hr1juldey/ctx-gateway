# ctx-gateway

**One governed endpoint between your agents and your tool estate.**

Agents fail on real business processes not because models are weak, but because they drown in context that carries no judgment: connect a handful of MCP servers and tens of thousands of tokens of tool definitions load before the agent reads its first user message — none of which tells it which tool matters *for this task*.

`ctx-gateway` federates any number of MCP servers behind a single MCP endpoint with a capability graph in between:

- **Capability registry** — every upstream tool, indexed and searchable
- **Per-task subgraph selection** — only the tools that matter for this request enter the agent's context
- **Token budget enforcement** — hard cap on context consumed by tool definitions, measured per request
- **Failure isolation** — one dead upstream server degrades a capability, never the workflow
- **Chain orchestration** — multi-server tool chains executed by the gateway, not narrated by the model

```
                    ┌──────────────────────────────────────────────┐
                    │                 ctx-gateway                  │
   agent ── MCP ──▶ │  registry ──▶ subgraph ──▶ budget ──▶ chain  │ ── MCP ──▶ server 1..N
                    └──────────────────────────────────────────────┘
```

## Why

In production at a consumer-health organization, the pattern behind this repo cut organization-wide LLM token consumption by **~93%** — a 15× reduction — while the platform became the default way agents access internal tools. This repo is the clean-room, open-source core of that architecture: same ideas, fresh code, reproducible benchmarks.

## Quickstart

```bash
# TODO(day 1): docker compose with 3 example upstream MCP servers
docker compose up
# point any MCP client at ws://localhost:8765
```

## Benchmark

The benchmark answers one question: **what does the agent's context pay for tool access?**

| setup | tool-def tokens in context | task success | p95 latency |
|---|---|---|---|
| naive: N servers direct | TBD | TBD | TBD |
| ctx-gateway, budget=2k | TBD | TBD | TBD |

Reproduce: `make bench` (TODO day 9).

## Status

Day 0 scaffold — see [BUILDLOG.md](BUILDLOG.md) for the 14-day public build. Design doc: [DESIGN.md](DESIGN.md). Roadmap: [ROADMAP.md](ROADMAP.md).

License: MIT (decide day 1).
