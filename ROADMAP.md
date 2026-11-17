# ctx-gateway — product roadmap

The line that separates this from everything else: model gateways (LiteLLM, Portkey) route between **models**. ctx-gateway routes between **tools and context** — it decides what the agent is allowed to see of your tool estate, per task, under a token budget. Nobody owns that layer in the open.

## Non-goals (deliberate)

- Not an agent framework. No prompt orchestration, no agent loops — any MCP client stays the brain.
- Not a model gateway. No LLM API routing/fallback.
- Not a marketplace. Federates *your* servers; hosts nothing.

---

## v0.1 — FEDERATE *(days 1–3)*
One MCP endpoint in front of N upstream MCP servers.

- Registry: connect upstreams (stdio/HTTP), enumerate capabilities, expose as one server.
- Docker-compose demo: 3 upstreams (filesystem, fetch, sqlite).
- **Exit test:** an unmodified MCP client lists and calls tools across all upstreams through one endpoint.

## v0.2 — SELECT *(days 4–7)*
The agent stops seeing everything.

- Capability index (descriptions + schema digests; embeddings optional).
- Per-task subgraph routing: retrieve the tools that matter for the request; serve only those defs.
- Token budget: hard cap on tool-def context; router must fit under it.
- **Benchmark goes live:** naive vs gateway at 5 / 20 / 50 upstreams — tool-def tokens in context, task success rate, p95 latency.

## v0.3 — SURVIVE *(days 8–10)* ← **the version Trail sees**
Production posture.

- Failure isolation: per-upstream circuit breakers, health, retries; one dead upstream degrades a capability, never the workflow.
- Chain execution: gateway executes multi-server tool chains (bounded steps, per-step budget).
- `make bench` + `make demo`: one command each, reproducible by any evaluator.
- **Exit test:** kill an upstream mid-benchmark → workflow completes, cost table unchanged.

## v0.4 — EXPLAIN *(days 11–14)*
Distribution.

- Rendered architecture diagram; 60-second animated explainer (why agents drown).
- BUILDLOG essay → launch post (HN / r/LocalLLA / LinkedIn).
- **Goal: first strangers running it.**

## v1.0 — ADOPTABLE *(weeks 3–6)*
Make it usable by people who owe you nothing.

- Per-upstream auth (API key/OAuth), config-as-code (YAML), streaming, WebSocket+stdio transports.
- Connector packs for upstreams people actually run (GitHub, Postgres, Slack, Sentry…).
- Packaging: `pipx install` / single docker image; docs.
- **Goal: first external issue/PR — the "repos people use" threshold.**

## v1.5 — OBSERVE *(months 2–3)*
Token spend as a first-class observable.

- Per-request telemetry: tokens per task per upstream, latency, failures, cost attribution.
- Prometheus export + simple dashboard (ML metrics surfaced so a decision-maker can act on them).
- This is the consulting audit (`"where does your agent spend leak"`) productized as software.

## v2.0 — LEARN *(months 3–5)*
The router stops being a heuristic.

- Fine-tuned small model replaces retrieval for subgraph selection + tool-call policy; runs on CPU/consumer GPU (local inference by design).
- Benchmark v2: learned vs retrieval router — selection accuracy, tokens, latency.
- **The research artifact** — HF Space hosting the live comparison; this is the tuning skill made visible.

## v3.0 — GOVERN *(months 5+)*
From tool context to judgment context.

- Policies attached to capabilities: who may call what, under which conditions; human-approval gates; exceptions that encode institutional knowledge.
- The governed graph: not just "which tools fit this task" but "which calls this business allows."
- Audit trail per decision.
- The open, self-hostable version of the layer every agent platform will need.

---

## Success metrics

| phase | the number that matters |
|---|---|
| v0.2 | tool-def tokens in context: ≥10× reduction at task-success parity |
| v0.3 | kill-an-upstream → zero failed workflows |
| v1.0 | first external contributor |
| v2.0 | learned router beats retrieval on selection accuracy at equal latency budget |
| v3.0 | a policy violation correctly blocked, in the demo, on camera |
