# AI Usage and Code Attribution

## Overview

Generative AI tools were used to assist with the development, testing, debugging, and documentation of the Agentic AI CTF Solver.

Claude (Anthropic) assisted with the original agent implementation, while ChatGPT (OpenAI) subsequently assisted with improvements to conversation management, Docker networking, service-readiness checks, and evaluation documentation.

All AI-assisted code was reviewed, modified where necessary, and tested by the team before integration.

## 1. Original Agent Development — Claude (Anthropic)

| File or Component | AI Assistance Provided |
|---|---|
| Project structure and workstation setup | Folder structure, Python environment, Docker Desktop installation, and macOS troubleshooting |
| `agent/Dockerfile.solver` | Non-root solver image, CTF tooling, and architecture compatibility |
| `agent/sandbox.py` | Docker and local sandbox backends, network isolation, path validation, and timeouts |
| `agent/tools.py` | Tool definitions, input validation, output limits, and error handling |
| `agent/agent_loop.py` | Autonomous agent loop, resource limits, and system prompt drafting |
| `controller/config.py` | Centralized configuration, resource limits, and configuration snapshots |
| `controller/challenge.py` | Challenge loading, flag protection, and contestant-file staging |
| `controller/evaluator.py` | Flag verification, submission handling, and logging |
| `controller/trace.py` | JSONL event logging and output handling |
| `controller/runner.py` | Multi-challenge evaluation, fresh workspaces, and result recording |
| `controller/summary.py`, `controller/plots.py` | Statistical summaries, metrics, and visualization |
| `scripts/check_gateway.py` | Gateway connectivity and model verification |

AI tool: Claude (Anthropic)

Development period: November 2026

Supporting conversation:

https://claude.ai/share/590dbddf-8423-4731-a9b7-6c84222aed97

These entries describe the development assistance reported by the team. Individual implementation details should be checked against the final source code.

## 2. Subsequent Agent Improvements — ChatGPT (OpenAI)

| File or Component | AI Assistance Provided |
|---|---|
| `agent/agent_loop.py` | Conversation-history trimming, investigation notes, and debugging |
| `agent/sandbox.py` | Configurable private Docker networking |
| `controller/runner.py` | Service-based challenge support and readiness-check integration |
| `controller/service_health.py` | Automated service-readiness validation |
| `scripts/start_pwn_get_it.sh` | Original vulnerable Docker service setup |
| `evidence/pwn-get-it/` | Comparison evidence, sanitized traces, and failure analysis |
| `comparison_report.md` | Experimental interpretation and comparison limitations |
| `README.md` | Installation instructions, project documentation, and reproducibility guidance |

AI tool: ChatGPT (OpenAI, GPT-6)

Development period: November 2026

Supporting conversation:

https://chatgpt.com/share/e/6af3ffb5-4960-83ea-b382-8c0d9c07a982

The AI-assisted recommendations and code were incorporated into the project after testing and review.

## 3. Autonomous CTF-Solving Model

Claude Haiku 5.5 was used through Duke AI Gateway as the language model powering the autonomous CTF-solving agent.

The model analyzed challenges, selected tools, executed investigations through the controller, and submitted candidate flags.

This evaluation role is separate from using Claude or ChatGPT as development assistants.

## 4. Code Attribution and Verification

Several source files received assistance from both AI tools at different development stages.

For example:

- `agent/agent_loop.py`: Claude assisted with the original agent loop; ChatGPT assisted with subsequent conversation-management improvements.
- `agent/sandbox.py`: Claude assisted with the original sandbox implementation; ChatGPT assisted with configurable Docker networking.
- `controller/runner.py`: Claude assisted with the original evaluation runner; ChatGPT assisted with service-based challenge integration and readiness checks.

For AI-generated code exceeding five lines, the supporting conversation links are provided as additional documentation.

Exact generation timestamps should be verified from the original conversations where required.

The team remains responsible for reviewing, testing, and validating the submitted code and reported results.
