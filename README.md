
# Agentic CTF Solver

An autonomous Capture-the-Flag (CTF) solving agent powered by Claude Haiku 5.5 through the Duke AI Gateway, with Docker-isolated execution, automated challenge investigation, and controller-side flag verification.

The system uses a language model to analyze CTF artifacts, execute commands, develop solutions, and submit candidate flags. A trusted Python controller manages tool execution, resource limits, execution traces, and verification.

This project was developed and evaluated using the NYU CTFTiny benchmark.

## Final Competition Configuration

The final competition version uses the latest working implementation maintained in the `main` branch of this repository.

The agent uses Claude Haiku 5.5 through Duke AI Gateway, Docker-isolated command execution, controller-side flag verification, conversation-history management, and automated service-readiness checks for supported network-based challenges.

The configured resource limits are 40 model steps, 600,000 total tokens, and 1,200 seconds per attempt.

To run the current agent, follow the Installation and Setup and Running the Evaluation sections below.

Historical source snapshots and evaluation configurations are preserved in `evaluation_config/`. The original 30-attempt evaluation and later improvement experiments are documented separately.

The original evaluation achieved 26/30 verified solves (86.67%). However, this result was obtained before all current improvements were implemented and should not be interpreted as the measured success rate of the final competition version.

AI-assisted development and code attribution are documented in [AI_USAGE.md](AI_USAGE.md).

The exact final Git commit should be recorded after the team freezes the competition version.

## Evaluation Highlights

| Metric | Result |
|---|---:|
| Evaluation dataset | NYU CTFTiny |
| Challenges evaluated | 10 |
| Trials per challenge | 3 |
| Total attempts | 30 |
| Verified solves | 26 |
| Overall success rate | 86.67% |
| Mean token consumption | 64,449 |
| Mean wall-clock time | 85.20 seconds |
| Model | Claude Haiku 5.5 |

These results represent the original recorded evaluation. They are not a guarantee of performance on other challenges.

The repository also includes later improvements to Docker networking, conversation management, and challenge-service readiness checks. These improvements were evaluated separately.

## System Architecture

```text
                  Claude Haiku 5.5
                         |
                    Duke AI Gateway
                         |
                  Python Agent Loop
                         |
                   Tool Dispatcher
                    /          \
                   /            \
          Docker Sandbox     Flag Verifier
           /challenge         (Controller)
              /work               |
                |             Expected Flag
           CTF Artifacts         (Private)
```

The language model communicates with Duke AI Gateway through the host-side Python controller.

Commands selected by Claude execute inside a restricted Docker container.

Expected flags and verification logic remain outside the solver container.

For service-based challenges, the solver can communicate with a separate vulnerable Docker service through a private Docker network.

## Features

- Autonomous CTF investigation using language-model tool calling.
- Support for cryptography, reverse engineering, and other supported CTFTiny challenges.
- Docker-based command execution with configurable network isolation.
- Read-only challenge files and a separate writable workspace.
- Three agent tools: `run_command`, `read_file`, and `submit_flag`.
- Trusted controller-side flag verification.
- Configurable model steps, token budgets, and execution timeouts.
- Fresh workspace and Docker container for every attempt.
- JSONL execution traces and evaluation results.
- Sequential multi-challenge evaluation with resume support.
- CSV and JSON statistical summaries.
- Conversation-history trimming and investigation notes.
- Private Docker networking for service-based challenges.
- Automated service-readiness checks before starting Claude.

## Repository Structure

```text
agentic-ctf-solver/
|
|-- agent/
|   |-- Dockerfile.solver
|   |-- __init__.py
|   |-- agent_loop.py
|   |-- sandbox.py
|   `-- tools.py
|
|-- controller/
|   |-- __init__.py
|   |-- challenge.py
|   |-- config.py
|   |-- evaluator.py
|   |-- plots.py
|   |-- runner.py
|   |-- service_health.py
|   |-- summary.py
|   `-- trace.py
|
|-- evaluation_config/
|   |-- README.md
|   |-- agent_loop.py
|   |-- agent_loop_paced_hash.txt
|   |-- challenge.py
|   |-- config.py
|   |-- evaluator.py
|   |-- final_reproducibility_manifest.txt
|   |-- pacing_change.txt
|   |-- run_configuration.txt
|   |-- runner.py
|   |-- sandbox.py
|   |-- source_hashes.txt
|   |-- tools.py
|   `-- trace.py
|
|-- evidence/
|   `-- pwn-get-it/
|       |-- README.md
|       |-- annotated_failure_analysis.md
|       |-- comparison_results.csv
|       |-- comparison_results.json
|       |-- configuration_notes.md
|       |-- docker_error.log
|       |-- source_hashes.txt
|       |-- traces/
|       |   |-- file_only_summary.jsonl
|       |   |-- broken_service_summary.jsonl
|       |   `-- fixed_service_summary.jsonl
|       `-- readiness-check/
|           |-- README.md
|           |-- readiness_results.json
|           `-- readiness_trace.jsonl
|
|-- results_docker/
|   |-- final_summary.csv
|   |-- final_summary.json
|   `-- final_evaluation_sanitized.csv
|
|-- scripts/
|   |-- check_gateway.py
|   `-- start_pwn_get_it.sh
|
|-- comparison_report.md
|-- generate_summary.py
|-- requirements.txt
|-- .gitignore
`-- README.md
```

The `agent/` and `controller/` directories contain the active implementation.

The Python files inside `evaluation_config/` are historical snapshots retained for evaluation documentation. They are not the active code.

Raw execution traces, private verifier files, temporary workspaces, and API credentials are excluded from the published repository.

## Requirements

- Linux or Windows with WSL2.
- Python 3.12 or a compatible Python 3 version.
- Docker Engine or Docker Desktop with WSL integration.
- Git.
- Access to Duke AI Gateway or a compatible model API endpoint.
- NYU CTFTiny dataset.
- Python dependencies listed in `requirements.txt`.

The evaluation used:

- Python 3.12.3
- Docker 28.4.0
- Claude Haiku 5.5
- Duke AI Gateway

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/vkbhanushali/agentic-ctf-solver.git
cd agentic-ctf-solver
```

### 2. Create a Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

The project uses the `nyuctf` package for loading CTFTiny challenge metadata.

### 3. Configure Duke AI Gateway

Create a `.env` file in the parent project directory, or adjust the environment-loading path in `controller/runner.py`.

Example:

```dotenv
DUKE_API_KEY=your_api_key_here
DUKE_MODEL=claude-haiku-5-5
DUKE_BASE_URL=https://litellm.oit.duke.edu/v1
```

Duke AI Gateway requires appropriate institutional access.

Connect to Duke VPN when required.

Never commit `.env` or API credentials to GitHub.

### 4. Build the Docker Solver Image

```bash
docker build -t ctf-solver:local -f agent/Dockerfile.solver agent/
```

Verify:

```bash
docker image inspect ctf-solver:local
```

The controller uses `ctf-solver:local` as its default solver image.

### 5. Prepare the CTFTiny Dataset

Clone the NYU CTFTiny repository:

```bash
git clone https://github.com/NYU-LLM-CTF/CTFTiny.git
```

Check out the dataset version used during development:

```bash
cd CTFTiny
git checkout f1c9531672c45b24b7fb5f3aa44a7ac33d3602f8
```

The original project used this directory structure:

```text
Finals/
|-- external/
|   `-- CTFTiny/
|       |-- ctftiny.json
|       `-- ctftiny/
|
`-- docker_adaptation/
    `-- ctf-agent-main/
```

If your directory structure differs, update the dataset path in `controller/runner.py`.

Only contestant-facing challenge files should be staged into the solver environment.

Expected flags and private metadata must remain outside the agent's direct access.

## Agent Configuration

The main configuration is stored in `controller/config.py`.

| Setting | Configured value |
|---|---:|
| Model | `claude-haiku-5-5` |
| Maximum model steps | 40 |
| Maximum wall-clock time | 1,200 seconds |
| Maximum total tokens | 600,000 |
| Maximum response tokens | 4,096 |
| Tool timeout | 60 seconds |
| Maximum tool output | 8,000 characters |
| Solver Docker image | `ctf-solver:local` |

The agent also uses request pacing to reduce repeated HTTP 429 errors from Duke AI Gateway.

The current request-pacing interval is 25 seconds between model requests.

## Docker Isolation

For ordinary file-based challenges, the solver container uses:

```text
--network none
--read-only
--user 10001:10001
--cap-drop ALL
--security-opt no-new-privileges
--memory 512m
--memory-swap 512m
--cpus 1
--pids-limit 64
```

Filesystem layout:

| Path | Access | Purpose |
|---|---|---|
| `/challenge` | Read-only | Contestant-facing files |
| `/work` | Writable | Temporary scripts and analysis |
| Controller filesystem | Not mounted | Verification and orchestration |

Each attempt receives a fresh container and workspace.

For supported service-based challenges, the solver uses a designated private Docker network instead of `--network none`.

These controls reduce risk but do not guarantee complete sandbox security.

## Running Service-Based Pwn Challenges

Some CTFTiny binary exploitation challenges require a running vulnerable service rather than only the provided binary.

For `pwn-get-it`, the project supports two Docker containers:

1. Solver container: Executes Claude's investigation and exploit commands.
2. Vulnerable service container: Runs the original challenge binary and provides the intended flag-retrieval environment.

Both containers communicate through the private Docker network `ctf-pwn-test`.

### Start the Vulnerable Service

First, ensure the original CTFTiny dataset is available at the expected location.

Run:

```bash
bash scripts/start_pwn_get_it.sh
```

The script:

- Builds the original challenge Docker image.
- Creates the private Docker network.
- Starts the vulnerable service.
- Enables the required `SETUID` and `SETGID` capabilities.
- Keeps the service port private.

The service listens on port `1437`.

### Run the Agent

```bash
python -m controller.runner \
  --challenges pwn-get-it \
  --trials 1 \
  --model claude-haiku-5-5 \
  --results results_docker/pwn_get_it_test.jsonl \
  --sleep 0
```

The runner connects the solver to the vulnerable service through the private Docker network.

The expected flag is not directly mounted into the solver container.

### Stop the Service

```bash
docker rm -f ctf-get-it-service
```

### Verified Pwn Result

The agent successfully solved `pwn-get-it` after the original challenge environment was configured correctly.

| Metric | Result |
|---|---:|
| Status | Solved |
| Verified | True |
| Model steps | 10 |
| Tokens | 79,516 |
| Runtime | 226.48 seconds |

This was a separate experiment and is not included in the original 30-attempt evaluation.

## Automated Docker Service Readiness Checks

The controller includes `controller/service_health.py`.

Before starting Claude on `pwn-get-it`, the controller checks whether the vulnerable service returns its expected startup prompt.

This prevents the agent from spending model tokens investigating a service that is unavailable or incorrectly configured.

The readiness checker was tested against:

| Test | Result |
|---|---|
| Working service | Accepted |
| Unavailable TCP port | Rejected |
| Broken `socat` service | Rejected |
| Stopped service | Controller terminated before model execution |

In the full runner test:

| Metric | Result |
|---|---|
| Status | `infrastructure_error` |
| Runtime | 1.684 seconds |
| Model events recorded | 0 |
| Token count | Not recorded (`null`) |

The earlier broken-service attempt consumed 265,293 tokens and lasted 976.23 seconds.

These results demonstrate that service validation can prevent unnecessary model execution. They are not a fully controlled performance comparison because the failure conditions differed.

See [Readiness Check Evidence](evidence/pwn-get-it/readiness-check/README.md).

## Running the Evaluation

### Dry Run

Preview the planned attempts without calling the model:

```bash
python -m controller.runner \
  --challenges cry-babycrypto cry-ecxor \
  --trials 3 \
  --dry-run
```

### Single Challenge

```bash
python -m controller.runner \
  --challenges cry-babycrypto \
  --trials 3 \
  --model claude-haiku-5-5 \
  --results results_docker/attempts.jsonl \
  --sleep 70
```

### Original 10-Challenge Evaluation

```bash
python -m controller.runner \
  --challenges \
  cry-babycrypto \
  cry-ecxor \
  cry-collision-course \
  for-1black0white \
  for-whyos \
  rev-baby-mult \
  rev-beleaf \
  rev-checker \
  rev-ezbreezy \
  rev-rebug-2 \
  --trials 3 \
  --model claude-haiku-5-5 \
  --results results_docker/final_evaluation.jsonl \
  --sleep 70
```

The runner executes attempts sequentially.

Each attempt uses a fresh model conversation and Docker workspace.

The runner supports resuming interrupted evaluations by skipping challenge/trial combinations already recorded in the selected results file.

Important: The current agent includes improvements made after the original evaluation. Rerunning this command does not guarantee identical results.

## Original Evaluation Results

The original evaluation used 10 CTFTiny challenges with three attempts each.

| Challenge | Verified solves | Success rate |
|---|---:|---:|
| babycrypto | 3/3 | 100% |
| ECXOR | 3/3 | 100% |
| Collision Course | 3/3 | 100% |
| 1black0white | 2/3 | 66.7% |
| whyOS | 0/3 | 0% |
| baby_mult | 3/3 | 100% |
| beleaf | 3/3 | 100% |
| checker | 3/3 | 100% |
| ezbreezy | 3/3 | 100% |
| rebug 2 | 3/3 | 100% |
| **Overall** | **26/30** | **86.67%** |

### Statistical Results

- Overall sample standard deviation of binary success outcomes: 0.3457.
- Mean token consumption: 64,449 tokens per attempt.
- Mean wall-clock time: 85.20 seconds per attempt.
- Four attempts ended without a verified solve.

Detailed evaluation results:

- `results_docker/final_summary.csv`
- `results_docker/final_summary.json`
- `results_docker/final_evaluation_sanitized.csv`

The sanitized CSV contains the 30 recorded attempts without private flags, raw model responses, or tool outputs.

### Evaluation Limitations

The original evaluation encountered Duke Gateway HTTP 429 rate limiting.

At least two `whyOS` attempts were confirmed to have ended after repeated HTTP 429 responses.

A 25-second minimum interval between model requests was introduced during the original evaluation to reduce rate limiting.

Therefore, all 30 attempts were not conducted under one unchanged configuration.

The 86.67% success rate should be interpreted as the observed result of the recorded evaluation, not a controlled measurement of one fixed agent configuration.

## Comparison and Improvement Experiments

After the original evaluation, we investigated additional challenges and improved the Docker environment.

### pwn-get-it Docker Comparison

Three configurations were tested:

1. File-only Docker environment.
2. Original vulnerable service with incorrect permissions.
3. Corrected vulnerable service with the required capabilities.

| Configuration | Verified | Steps | Tokens | Runtime |
|---|---|---:|---:|---:|
| File-only Docker | No | 40 | 331,623 | 976.93s |
| Broken service | No | 40 | 265,293 | 976.23s |
| Corrected service | Yes | 10 | 79,516 | 226.48s |

The broken service failed because `socat` could not switch to the restricted challenge user.

Docker logs showed:

```text
socat E initgroups(get_it, 1000): Operation not permitted
```

After enabling the required Docker capabilities, the vulnerable program started correctly and the agent recovered a verified flag.

Compared with the broken-service attempt, the successful run used approximately 70% fewer tokens and 77% less execution time.

These are single-run observations, not statistically established improvements.

### Supporting Evidence

- [Comparison Report](comparison_report.md)
- [Experiment Evidence](evidence/pwn-get-it/README.md)
- [Annotated Failure Analysis](evidence/pwn-get-it/annotated_failure_analysis.md)
- [Configuration Notes](evidence/pwn-get-it/configuration_notes.md)
- [Readiness Check Results](evidence/pwn-get-it/readiness-check/README.md)

The evidence directory includes sanitized traces, result summaries, configuration notes, and Docker error documentation.

## Generating Evaluation Summaries

After completing an evaluation, run:

```bash
python generate_summary.py
```

The script reads:

```text
results_docker/final_evaluation.jsonl
```

and generates:

```text
results_docker/final_summary.csv
results_docker/final_summary.json
```

The summaries include overall and per-challenge success rates, sample standard deviations, mean token consumption, and mean wall-clock times.

The original raw evaluation file is retained locally and is not published to GitHub.

## Reproducibility

The repository includes historical evaluation configuration files and a current reproducibility manifest.

See:

- [Evaluation Configuration](evaluation_config/README.md)
- [Final Reproducibility Manifest](evaluation_config/final_reproducibility_manifest.txt)

The manifest records:

- Git source commit.
- Python and Docker versions.
- Solver and vulnerable-service image identifiers.
- Source file hashes.
- NYU CTFTiny dataset commit.
- Model and evaluation settings.

CTFTiny dataset commit:

```text
f1c9531672c45b24b7fb5f3aa44a7ac33d3602f8
```

The original evaluation used an earlier agent configuration. Historical snapshots are retained in `evaluation_config/`.

The current implementation includes subsequent changes to conversation handling, Docker networking, and readiness checks.

For new controlled evaluations, freeze the model, code, challenge set, Docker images, budgets, and request-pacing configuration before collecting results.

## Security and Responsible Use

This project is intended for authorized CTF challenges and academic cybersecurity research.

Security controls include:

- Docker isolation.
- Read-only contestant files.
- Restricted container permissions.
- Private networking for supported service-based challenges.
- Controller-side flag verification.
- Model step, token, and runtime budgets.
- Execution traces and infrastructure error reporting.

The solver does not receive Duke API credentials or private verifier metadata.

For service-based challenges, the intended vulnerable service may expose the challenge flag through successful exploitation, but the solver does not receive the flag file as a direct mount.

Do not use this system against infrastructure or applications without authorization.

## Acknowledgments

- NYU CTFTiny and NYU CTF Bench for challenge datasets and tooling.
- Duke AI Gateway for model access.
- Docker for isolated execution.
- Claude Haiku 5.5 as the language model used in evaluation.

## Author

Varun Bhanushali, Atharva Jog, Shwetta Mittal, Deekshitha Manjunatha Reddy

## Project Status

The autonomous CTF agent, Docker integration, service-based pwn support, and automated readiness checks are implemented.

The original evaluation recorded 30 attempts with 26 verified solves (86.67%).

Additional Docker experiments, failure analyses, and reproducibility evidence are documented separately.

Future improvements include broader service-based challenge support, more efficient model reasoning, improved Gateway rate-limit handling, and fully controlled multi-trial comparisons.
