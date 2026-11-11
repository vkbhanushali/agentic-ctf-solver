# Evaluation Configuration and Historical Snapshots

This directory preserves configuration records and source-code snapshots
from the original CTFTiny evaluation.

## Original Evaluation

- Dataset: NYU CTFTiny
- Model: Claude Haiku 5.5 through Duke AI Gateway
- Challenges: 10
- Trials per challenge: 3
- Total attempts: 30
- Verified solves: 26
- Overall success rate: 86.67%

## Historical Source Files

The Python files in this directory are historical copies used to document
the earlier evaluation configuration.

Examples:
- agent_loop.py
- sandbox.py
- runner.py
- evaluator.py
- config.py
- tools.py
- challenge.py
- trace.py

These files are not the active implementation.

## Active Implementation

Use the following directories when running the current agent:

- agent/ — Active solver and Docker sandbox
- controller/ — Active evaluation runner and verification
- scripts/ — Gateway checks and Docker service setup

Do not run the historical Python files from evaluation_config/.

## Configuration Records

- run_configuration.txt — Original evaluation settings
- pacing_change.txt — Request-pacing modification
- source_hashes.txt — Historical source hashes
- agent_loop_paced_hash.txt — Hash after pacing modification
- final_reproducibility_manifest.txt — Current environment and source versions

## Important Reproducibility Note

The original 30-attempt evaluation used an earlier agent configuration.

Request pacing was modified during the original evaluation to address
Duke Gateway HTTP 429 rate limiting.

The current GitHub implementation includes later improvements such as
conversation trimming, service-based Docker networking, and automated
service readiness checks.

Therefore, the original 26/30 evaluation should not be presented as
having been produced by the current agent configuration.

The original evaluation results and later experiments are reported
separately.

## Final Configuration Selection

The final competition implementation is maintained in the active `agent/` and `controller/` directories on the GitHub `main` branch.

The historical Python source snapshots in this directory document the original evaluation and should not be executed as the current agent.

The final implementation includes conversation-history management, Docker networking for supported service-based challenges, and automated service-readiness checks. These improvements were introduced after the original 30-attempt evaluation.

The `final_reproducibility_manifest.txt` file records the source revision, Python and Docker versions, image identifiers, source hashes, and CTFTiny dataset version at the time the manifest was generated.

Because subsequent documentation and code changes may have occurred, the manifest's recorded commit should not automatically be treated as the final competition commit. The team should record the final frozen revision separately before submission.
