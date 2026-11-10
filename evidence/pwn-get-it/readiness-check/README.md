# Automated Docker Service Readiness Check

## Objective

Prevent the CTF agent from wasting Duke AI Gateway tokens on unavailable or incorrectly configured challenge services.

## Problem

During the original pwn-get-it experiment, the agent spent 265,293 tokens and 976.23 seconds investigating a service that accepted TCP connections but could not launch its vulnerable program.

Docker logs revealed:

    socat E initgroups(get_it, 1000): Operation not permitted

## Improvement

We implemented controller/service_health.py to check whether the challenge service returns its expected startup prompt before starting Claude.

For pwn-get-it, the expected prompt is:

    Do you gets it??

The controller records the readiness result and raises an infrastructure error if the check fails.

## Readiness Tests

| Test | Expected | Observed | Result |
|---|---|---|---|
| Working service, port 1437 | Accept | Ready: True | Pass |
| Unavailable port 1438 | Reject | ConnectionRefusedError | Pass |
| Broken socat service | Reject | Challenge prompt not received | Pass |
| Stopped service, full runner | Reject before Claude | infrastructure_error | Pass |

## Full Runner Test

- Challenge: pwn-get-it
- Model: Claude Haiku 5.5
- Status: infrastructure_error
- Runtime: 1.684 seconds
- Model events recorded: 0
- Token count: Not recorded (null)
- Gateway requests observed in trace: 0

The service-health trace recorded:

1. attempt_begin
2. service_health (ready: false)
3. attempt_error (RuntimeError)

The stopped service caused a DNS resolution failure.

## Before-and-After Observation

| Metric | Earlier broken-service attempt | Readiness-check test |
|---|---:|---:|
| Runtime | 976.23 seconds | 1.684 seconds |
| Tokens | 265,293 | Not recorded |
| Failure classification | max_steps | infrastructure_error |
| Model activity | Yes | None recorded |

The readiness check rejected the unavailable service approximately 99.83% faster than the earlier failed attempt completed.

These experiments used different failure conditions and were not a controlled performance comparison.

## Evidence

- readiness_results.json: Structured runner result
- readiness_trace.jsonl: Sanitized controller trace
- ../docker_error.log: Original service permission failure
- ../annotated_failure_analysis.md: Detailed failure analysis

## Limitations

The readiness check currently supports pwn-get-it specifically.

It verifies the expected startup prompt, not whether exploitation will succeed.

The standalone broken-service test and full-runner stopped-service test used different failure conditions.

No model events were recorded during the early-exit test, but the result file stores total_tokens as null rather than zero.

## Decision

Retain the readiness check for pwn-get-it and extend the approach to other service-based challenges when their expected startup behavior is known.
