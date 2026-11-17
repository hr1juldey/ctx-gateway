# INTEGRATIONS — proving fluency in *their* tooling

The gateway is the thesis; these are the receipts that we speak their stack natively.

## Trail — Trail-Code (github.com/trailhq/Trail-Code, 11.3k★)

Trail-Code is the self-learning context layer for coding agents: a code map + team learnings that Claude Code / Cursor / Codex read before each session. Their published numbers: **46% fewer tool calls, 60% less time, +12% on SWE-bench Verified**.

Two artifacts, both real:

1. **Dogfood + measure (Day 7 onward).** `trail init` on ctx-gateway itself. Every dev session logged in BUILDLOG with/without the graft map: tool calls, tokens, time on my own tasks. Deliverable: *"Running Trail-Code on a fresh repo — an independent measurement."* Even n-small, an honest methodology writeup of THEIR product is the single strongest artifact a Trail application can contain.
2. **Compose (Day 8+).** ctx-gateway serves as the MCP tool layer beneath a Trail-Code-equipped agent: the agent gets its **code context** from Trail-Code and its **tool context** from ctx-gateway's subgraph routing — context layer × tool layer, which is literally the company thesis. Benchmark: same tasks, naive-tools vs gateway-routed, agent-with-map vs without.

Plus: docs/benchmark-scenario PRs upstream (TypeScript is not my lane; measurement is).

## Lexsi Labs (github.com/Lexsi-Labs — all Python, our lane)

| Repo | Why it fits | Contribution shape |
|---|---|---|
| **AgentTune** (agent post-training alignment) | agents + tuning — exactly the two skills we claim | eval-scenario PR / docs / a small harness improvement |
| **xai_evals** (eval matrices for explainability) | the proof-habit as a library | one new eval + notebook |
| **SafeTune / CircuitKIT** | safety/interp — stretch | read first, issue-quality discussions |

One merged PR in either repo >> a cover letter.

## Provider strategy (the "no providers beneath it" problem)

Three tiers — the benchmark never depends on anyone's API key:

1. **Reference servers** (real, keyless): filesystem, fetch, git, sqlite — the docker-compose demo.
2. **Fleet generator** (`providers/fleetgen.py`): FastMCP factory spinning N servers with realistic tool schemas, seeded and deterministic — the benchmark engine. Reproducible at N = 5 / 20 / 50 / 100. Synthetic-at-scale is how benchmarks are done; `make bench` running offline is a feature.
3. **Live third-party servers** (optional): env-var keys, an appendix row marked "real-world".
