## Comparison and Improvement: Docker Environment for Binary Exploitation

### 1. Problem and Hypothesis

During our initial evaluation, the CTF agent performed well on cryptography and reverse-engineering challenges but struggled with binary exploitation challenges such as `pwn-get-it`.

Initially, our Docker setup provided the agent with the challenge binary and analysis tools but no running vulnerable service. We later recreated the original CTFTiny service in a separate Docker container. However, the agent still failed because the service was not starting correctly.

Our hypothesis was that configuring the original vulnerable service correctly would allow the agent to interact with the challenge as intended and improve its ability to recover a verified flag.

### 2. Implementation and Experimental Setup

We tested three Docker configurations using Claude Haiku 5.5 through Duke AI Gateway.

| Configuration | Description |
|---|---|
| A: File-only Docker | Agent could analyze and execute the supplied binary locally, without access to the original vulnerable service. |
| B: Broken service Docker | Agent could connect to the challenge service, but Docker permissions prevented the vulnerable program from starting. |
| C: Corrected service Docker | Agent connected to the original vulnerable service through a private Docker network, with the necessary user-switching capabilities enabled. |

The corrected service configuration used `CAP_SETUID` and `CAP_SETGID`, allowing `socat` to launch the vulnerable binary under the intended restricted user.

The service's flag file was not directly mounted into the solver container. The agent had to recover the flag through interaction with the vulnerable service.

### 3. Results

| Metric | File-only | Broken service | Corrected service |
|---|---:|---:|---:|
| Verified solve | No | No | Yes |
| Model steps | 40 | 40 | 10 |
| Total tokens | 331,623 | 265,293 | 79,516 |
| Runtime (seconds) | 976.93 | 976.23 | 226.48 |

Compared with the broken service configuration, the corrected service used approximately 70% fewer tokens and 77% less execution time.

The corrected environment also enabled a verified solve in 10 steps, whereas the previous attempts exhausted the 40-step limit.

### 4. Trace Evidence and Failure Analysis

The failed service-based attempt showed that the agent was connecting to port 1437 and sending exploit payloads. However, connections repeatedly closed without returning useful output.

Inspecting the Docker service logs revealed:

```text
socat: initgroups(get_it, 1000): Operation not permitted
```

The issue occurred because the service container was launched with all Linux capabilities removed. This prevented `socat` from switching to the restricted challenge user.

After enabling `CAP_SETUID` and `CAP_SETGID`, the vulnerable service started successfully.

The successful agent trace recorded 10 model steps, including command execution and a final `submit_flag` call. The controller verified the submitted flag and recorded `status: solved` with `reason: verified_flag`.

### 5. Interpretation and Configuration Decision

The results indicate that correctly reproducing the challenge environment is important for evaluating autonomous agents on service-based CTF challenges.

The agent was capable of analyzing the binary in the original setup, but without a functional vulnerable service, it could not complete the intended exploitation workflow.

We retained the corrected two-container configuration for `pwn-get-it`, while keeping ordinary file-based challenges network-isolated.

### 6. Limitations

Each configuration was tested once, so the observed differences cannot establish a statistically reliable improvement in success rate.

The file-only and service-based configurations also differed in their available infrastructure, and the agent underwent development changes during the broader experimentation process. Therefore, the results should be interpreted as an engineering comparison rather than a fully controlled experiment.

Additional repeated trials under a frozen configuration would be needed to measure reliability more rigorously.

### Conclusion

This experiment demonstrated that agent performance depends not only on the language model's reasoning but also on the environment provided for challenge execution.

Correcting the Docker service permissions allowed the original vulnerable program to start, enabling the agent to recover a verified flag in 10 steps using 79,516 tokens.

## Controlled Comparison Limitations

The original evaluation achieved 26 verified solves across 30 attempts (86.67%), while the updated agent successfully completed four regression attempts on ECXOR and beleaf.

The Docker experiments showed that correcting the `pwn-get-it` service environment enabled a verified solve in 10 model steps using 79,516 tokens. The automated service-readiness check also detected unavailable or incorrectly configured services before starting Claude. In the full runner test, an unavailable service was detected in 1.684 seconds without any recorded model activity.

However, these experiments were not conducted as a fully controlled comparison of the original and updated agent versions. Several factors changed during development, including request pacing, conversation-history management, and Docker service availability. Each `pwn-get-it` configuration was also tested only once.

Therefore, the available evidence supports the effectiveness of specific infrastructure improvements and confirms that the updated agent can solve the tested regression challenges. It does not establish a statistically reliable improvement in overall success rate or token efficiency.

We selected the updated implementation for the final competition because it supports additional challenge environments and includes preventive infrastructure validation. A controlled multi-trial comparison under identical settings remains future work.
