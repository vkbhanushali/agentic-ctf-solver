# pwn-get-it — Docker Configuration Comparison

## Objective

Evaluate how the Docker challenge environment affects the ability of our Claude Haiku 5.5 CTF agent to solve the NYU CTFTiny `pwn-get-it` challenge.

## Hypothesis

Providing a correctly configured vulnerable service will allow the agent to complete the intended exploitation workflow, whereas a file-only environment or a service that cannot start correctly may prevent successful flag retrieval.

## Experimental Results

| Configuration | Verified | Steps | Tokens | Runtime |
|---|---|---:|---:|---:|
| File-only Docker | No | 40 | 331,623 | 976.93s |
| Broken service | No | 40 | 265,293 | 976.23s |
| Corrected service | Yes | 10 | 79,516 | 226.48s |

The corrected service produced a verified solve in 10 steps.

Compared with the broken service attempt, it used approximately 70% fewer tokens and 77% less runtime.

## Root Cause

The original service failed to start the vulnerable program because the Docker container lacked the capabilities required for user switching.

Observed Docker error:

    socat E initgroups(get_it, 1000): Operation not permitted

The service was corrected by enabling `CAP_SETUID` and `CAP_SETGID` while keeping the other capabilities dropped.

## Evidence Files

| File | Description |
|---|---|
| `comparison_results.csv` | Per-configuration results |
| `comparison_results.json` | Machine-readable results and trace references |
| `configuration_notes.md` | Setup differences, interpretation, and limitations |
| `docker_error.log` | Reconstructed Docker error excerpt |
| `source_hashes.txt` | SHA-256 hashes of private original evidence |
| `traces/file_only_summary.jsonl` | Sanitized file-only execution events |
| `traces/broken_service_summary.jsonl` | Sanitized broken-service execution events |
| `traces/fixed_service_summary.jsonl` | Sanitized successful execution events |
| `annotated_failure_analysis.md` | Detailed failure analysis with actual tool calls, results, Docker error, and implemented fix |

## Trace References

Original private traces:

- File-only: `pwn-get-it-t1-3f6f98a15376.jsonl`
- Broken service: `pwn-get-it-t1-fde217b84cc0.jsonl`
- Corrected service: `pwn-get-it-t1-a7450338ae57.jsonl`

The complete traces are retained privately. The published summaries omit model text, exploit commands, tool outputs, and flag values.

## Reproducibility

The corrected service can be started using:

    bash scripts/start_pwn_get_it.sh

Run this command from the repository root after downloading CTFTiny into the directory structure described in the main README.

The service is connected to the solver through the private `ctf-pwn-test` Docker network.

## Limitations

Each configuration was tested once. These results demonstrate an observed engineering improvement but do not establish a statistically reliable success-rate difference.

The agent implementation also evolved during experimentation, so the three runs should not be presented as a fully controlled comparison.

The original 26/30 CTFTiny evaluation remains separate from this experiment.
