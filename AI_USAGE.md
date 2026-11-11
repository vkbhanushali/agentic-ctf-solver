# AI Usage and Code Attribution

## Overview

Generative AI tools were used during the development, debugging, testing, and documentation of the Agentic AI CTF Solver project.

AI-generated code and recommendations were reviewed and modified before integration. The team remains responsible for the submitted implementation, experimental results, and conclusions.

## AI-Assisted Development

| File or component | AI tool | Assistance provided | Date |
|---|---|---|---|
| `agent/agent_loop.py` | ChatGPT | Conversation trimming, investigation notes, token management, and debugging guidance | November 2026 |
| `agent/sandbox.py` | ChatGPT | Configurable Docker networking and sandbox integration | November 2026 |
| `controller/runner.py` | ChatGPT | Service-based challenge configuration and readiness-check integration | November 2026 |
| `controller/service_health.py` | ChatGPT | Service-health validation and error-handling logic | November 10, 2026 |
| `scripts/start_pwn_get_it.sh` | ChatGPT | Docker service startup script and Linux capability configuration | November 10, 2026 |
| `evidence/pwn-get-it/` | ChatGPT | Evidence extraction scripts, sanitized trace summaries, and comparison documentation | November 2026 |
| `README.md` and project report | ChatGPT | Documentation organization, technical explanations, and drafting assistance | November 2026 |

Dates indicate the approximate development period and should be verified against Git history and conversation timestamps before submission.

The table identifies known ChatGPT-assisted components; it is not necessarily a complete inventory of all AI-generated code in the project.

## Example Code Attribution

The service-readiness implementation in `controller/service_health.py` was drafted with assistance from ChatGPT (OpenAI, GPT-6) on November 10, 2026. The code was integrated into the Python controller and tested against working, unavailable, and misconfigured Docker services.

The Docker service setup in `scripts/start_pwn_get_it.sh` was developed with ChatGPT assistance on November 10, 2026 and adjusted to support the original CTFTiny challenge environment.

## Supporting AI Conversation

ChatGPT development conversation:

https://chatgpt.com/share/e/6af3ffb5-4960-83ea-b382-8c0d9c07a982

This link is provided as supporting documentation for AI-assisted code and development discussions exceeding five lines.

## Autonomous Agent Model

Claude Haiku 5.5 was used through Duke AI Gateway as the model evaluated for autonomous CTF solving.

Its challenge-solving outputs were recorded in execution traces and evaluated by the trusted controller.

This is separate from the generative AI assistance used to develop and document the software.

## Verification and Responsibility

The team reviewed and tested AI-assisted code through Python syntax checks, Docker connectivity tests, controlled service-readiness checks, regression testing, and recorded CTF evaluation attempts.

The submitted source code, results, and analysis remain the responsibility of the project team.
