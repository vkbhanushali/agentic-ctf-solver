# Agentic CTF Solver

An autonomous Capture-the-Flag (CTF) solving agent powered by Claude Haiku 5.5 through the Duke AI Gateway, with isolated Docker execution and controller-side flag verification.

The system uses a language model to investigate CTF artifacts, execute analysis commands, formulate solutions, and submit candidate flags. A trusted Python controller manages the solver's tools, resource limits, execution traces, and verification.

## Evaluation Highlights

| Metric | Result |
|---|---:|
| Evaluation dataset | CTFTiny |
| Challenges | 10 |
| Independent trials per challenge | 3 |
| Total attempts | 30 |
| Verified solves | 26 |
| Overall success rate | 86.67% |
| Mean token consumption | 64,449 |
| Mean wall-clock time | 85.20 seconds |

These are observed end-to-end results from the recorded evaluation, not a guarantee of performance on other CTF challenges.

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
          Docker Sandbox    Flag Verifier
           /challenge       (Controller)
           /work                |
              |            Expected Flag
        CTF Artifacts       (Private)
```

The language model communicates with the Duke AI Gateway through the host-side Python controller. Commands selected by the model are executed inside a restricted Docker container.

Expected flags and verification logic remain outside the solver container.

## Features

- Autonomous, iterative CTF investigation using language-model tool calling.
- Support for cryptography, reverse engineering, forensics, and other file-based challenges.
- Docker-based command execution with network isolation.
- Read-only contestant files and a separate writable workspace.
- Three tools: `run_command`, `read_file`, and `submit_flag`.
- Trusted controller-side verification of submitted flags.
- Configurable model steps, wall-clock limits, and token budgets.
- Fresh workspace and Docker container for each attempt.
- JSONL execution traces and evaluation results.
- Sequential multi-challenge evaluation with resume support.
- CSV and JSON statistical summaries.

## Repository Structure

```text
agentic-ctf-solver/
├── agent/
│   ├── agent_loop.py
│   ├── sandbox.py
│   ├── tools.py
│   └── Dockerfile.solver
├── controller/
│   ├── challenge.py
│   ├── config.py
│   ├── evaluator.py
│   ├── runner.py
│   ├── summary.py
│   ├── plots.py
│   └── trace.py
├── evaluation_config/
│   ├── run_configuration.txt
│   ├── source_hashes.txt
│   └── pacing_change.txt
├── results_docker/
│   ├── final_summary.csv
│   └── final_summary.json
├── scripts/
│   └── check_gateway.py
├── generate_summary.py
└── README.md
```

Raw attempt traces, temporary workspaces, private verifier files, and API credentials are not included in the published repository.

## Requirements

- Linux or Windows with WSL2
- Python 3.12 or a compatible Python 3 version
- Docker Engine or Docker Desktop with WSL integration
- Git
- Access to a compatible LiteLLM/OpenAI-style API endpoint
- Access to the CTFTiny dataset
- Python packages: `requests`, `python-dotenv`, and `nyuctf` (the NYU CTF Bench Python package)

The exact installation method for `nyuctf` depends on the version of the NYU CTF Bench repository being used.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/vkbhanushali/agentic-ctf-solver.git
cd agentic-ctf-solver
```

### 2. Create a Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the Python dependencies:

```bash
python -m pip install -r requirements.txt
```

The controller also requires the `nyuctf` package used by `controller/challenge.py`. Install the compatible package from the NYU CTF Bench project before running the evaluation.

### 3. Configure the model API

Create a `.env` file in the parent project directory, or adjust the environment-loading path in `controller/runner.py` for your installation.

Example:

```dotenv
DUKE_API_KEY=your_api_key_here
DUKE_MODEL=claude-haiku-5-5
DUKE_BASE_URL=https://litellm.oit.duke.edu/v1
```

The Duke AI Gateway endpoint and model require appropriate institutional access. Users without Duke access must configure a compatible endpoint and model.

Never commit `.env` or API credentials to Git.

### 4. Build the Docker solver image

The solver Dockerfile is located at `agent/Dockerfile.solver`.

```bash
docker build -t ctf-solver:local -f agent/Dockerfile.solver agent/
```

Verify the image:

```bash
docker image inspect ctf-solver:local
```

The controller uses `ctf-solver:local` by default.

### 5. Prepare the CTFTiny dataset

Obtain the CTFTiny benchmark separately and place it in the expected directory structure.

The current runner expects the dataset at:

```text
Finals/
├── external/
│   └── CTFTiny/
│       ├── ctftiny.json
│       └── ctftiny/
└── docker_adaptation/
    └── ctf-agent-main/
```

If the project is cloned into another directory structure, update the `DATASET` path in `controller/runner.py`.

Challenge files are staged into isolated workspaces by `controller/challenge.py`. Only declared contestant-facing files should be provided to the solver.

## Configuration

The main configuration is stored in `controller/config.py`.

| Setting | Configured value | Purpose |
|---|---:|---|
| Model | `claude-haiku-5-5` | Language model |
| Maximum model steps | 40 | Model calls per attempt |
| Maximum wall-clock time | 1,200 seconds | 20-minute attempt limit |
| Maximum total tokens | 600,000 | Token budget per attempt |
| Maximum response tokens | 4,096 | Model output limit |
| Tool timeout | 60 seconds | Per-command timeout |
| Maximum tool output | 8,000 characters | Output truncation limit |
| Docker image | `ctf-solver:local` | Solver environment |

The runner uses a separate worker process for each attempt and enforces an additional outer deadline.

## Docker Isolation

The solver container is configured with the following restrictions:

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
| `/challenge` | Read-only | Contestant-facing challenge files |
| `/work` | Writable | Temporary scripts and analysis |
| Controller filesystem | Not mounted | Verification and orchestration |

Each attempt receives a fresh container and workspace. Containers are removed after execution.

These controls reduce exposure but are not a guarantee of complete sandbox security.

## Running Service-Based Pwn Challenges

Some CTFTiny binary exploitation challenges require a running vulnerable service rather than only the supplied binary.

For `pwn-get-it`, the project supports two separate Docker containers:

- Solver container (`ctf-solver:local`): Runs Claude's analysis commands and exploit scripts.
- Challenge container (`ctf-get-it:local`): Runs the original vulnerable service with the challenge flag.

Both containers communicate through the private Docker network `ctf-pwn-test`.

### Start the Challenge Service

First, download the original CTFTiny dataset and place it in the directory structure described above.

From the project root, run:

```bash
bash scripts/start_pwn_get_it.sh
```

The script builds the original challenge image, creates the private Docker network if necessary, and starts the vulnerable service with the required `SETUID` and `SETGID` capabilities.

The service listens on port `1437` within the Docker network. The port is not published to the host.

### Run the Agent

```bash
python -m controller.runner \
  --challenges pwn-get-it \
  --trials 1 \
  --model claude-haiku-5-5 \
  --results results_docker/pwn_get_it_test.jsonl \
  --sleep 0
```

The runner connects the solver container to the private challenge network and provides the service hostname and port to the agent.

The expected flag is not directly mounted into the solver container. The agent must interact with the vulnerable service to retrieve it.

### Stop the Service

After testing:

```bash
docker rm -f ctf-get-it-service
```

### Verified Test Result

Using the corrected original challenge environment, the agent successfully solved `pwn-get-it`:

| Metric | Result |
|---|---:|
| Status | Solved |
| Verified | True |
| Runtime | 226.48 seconds |
| Tokens | 79,516 |

This result is from a separate service-based experiment and is not included in the original 30-attempt evaluation.

## Running the Evaluation

### Dry run

Check the planned attempts without calling the model:

```bash
python -m controller.runner \
  --challenges cry-babycrypto cry-ecxor \
  --trials 3 \
  --dry-run
```

### Single challenge

```bash
python -m controller.runner \
  --challenges cry-babycrypto \
  --trials 3 \
  --model claude-haiku-5-5 \
  --results results_docker/attempts.jsonl \
  --sleep 70
```

### Full CTFTiny evaluation

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

The runner executes attempts sequentially. Each attempt receives a fresh model conversation and Docker environment.

The runner also supports resuming an interrupted evaluation by skipping challenge/trial combinations already recorded in the specified results file.

## Evaluation Results

The evaluation used 10 CTFTiny challenges, with three attempts per challenge.

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

The sample standard deviation uses binary outcomes, where a verified solve is 1 and an unsuccessful attempt is 0.

Detailed per-challenge statistics are available in `results_docker/final_summary.csv` and `results_docker/final_summary.json`.

### Evaluation Limitations

The evaluation encountered Duke Gateway HTTP 429 rate limiting. At least two `whyOS` attempts were confirmed to have ended after repeated HTTP 429 responses.

To reduce further rate limiting, a 25-second minimum interval between model requests was introduced during the evaluation.

Consequently, the 30 recorded attempts were not all performed under one unchanged configuration. The aggregate success rate should be interpreted as the observed result of this evaluation, not as a controlled measurement of one fixed agent configuration.

The evaluation uses local CTFTiny metadata for exact-match flag verification. It does not use an instructor-provided private verifier.

Some CTFTiny challenges also use nonstandard flag formats, which the agent should not assume are incorrect.

## Generating Evaluation Summaries

After completing the evaluation, run:

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

These contain overall and per-challenge success rates, sample standard deviations, mean token consumption, and mean wall-clock times.

## Reproducibility

The `evaluation_config/` directory records source hashes, the solver image ID, model settings, and the request-pacing change.

To verify recorded source hashes:

```bash
sha256sum -c evaluation_config/source_hashes.txt
```

Some source hashes represent the pre-pacing configuration. The current agent source may therefore differ from the original frozen snapshot.

For a new controlled evaluation, freeze the complete source configuration, Docker image, model, challenge set, and rate-limit policy before starting.

## Security and Responsible Use

This project is intended for authorized CTF challenges and academic security research.

The agent should operate only on challenge files explicitly provided for testing. The solver container has no external network access and does not receive API credentials or expected flags.

The controller retains responsibility for verification, resource limits, and execution logging.

Do not use this system against infrastructure or applications without authorization.

## Acknowledgments

- CTFTiny and NYU CTF Bench for challenge datasets and tooling.
- Duke AI Gateway for model access.
- Docker for isolated execution.
- Claude Haiku 5.5 as the language model used in the evaluation.

## Author

Varun Bhanushali

GitHub: https://github.com/vkbhanushali

## Project Status

Docker integration completed. Thirty CTFTiny evaluation attempts recorded, with 26 verified solves. Further work includes improving Gateway rate-limit handling, refining infrastructure-error classification, and running a fully frozen follow-up evaluation.
