import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

results_dir = Path("results_docker")
source = results_dir / "final_evaluation.jsonl"

records = [
    json.loads(line)
    for line in source.read_text(encoding="utf-8").splitlines()
    if line.strip()
]

groups = defaultdict(list)

for record in records:
    groups[record["challenge_id"]].append(record)


def summarize(attempts):
    outcomes = [int(r["verified"]) for r in attempts]

    tokens = [
        r["total_tokens"]
        for r in attempts
        if r.get("total_tokens") is not None
    ]

    times = [
        r["elapsed_s"]
        for r in attempts
        if r.get("elapsed_s") is not None
    ]

    return {
        "attempts": len(attempts),
        "solved": sum(outcomes),
        "success_rate": round(statistics.mean(outcomes), 4),
        "success_sd_sample": round(
            statistics.stdev(outcomes), 4
        ) if len(outcomes) > 1 else None,
        "mean_tokens": round(statistics.mean(tokens), 2)
        if tokens else None,
        "mean_wall_time_s": round(statistics.mean(times), 2)
        if times else None,
    }


summary = {
    "model": "claude-haiku-5-5",
    "total_challenges": len(groups),
    "overall": summarize(records),
    "per_challenge": {
        name: summarize(attempts)
        for name, attempts in sorted(groups.items())
    },
    "notes": [
        "All attempts used Docker isolation and Duke AI Gateway.",
        "Request pacing was changed during evaluation.",
        "Errors are counted as unsuccessful attempts.",
        "At least two whyOS attempts encountered HTTP 429.",
    ],
}

json_path = results_dir / "final_summary.json"
csv_path = results_dir / "final_summary.csv"

json_path.write_text(
    json.dumps(summary, indent=2) + "\n",
    encoding="utf-8",
)

with csv_path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)

    writer.writerow([
        "challenge",
        "attempts",
        "solved",
        "success_rate",
        "success_sd_sample",
        "mean_tokens",
        "mean_wall_time_s",
    ])

    for name, attempts in sorted(groups.items()):
        row = summarize(attempts)

        writer.writerow([
            name,
            row["attempts"],
            row["solved"],
            row["success_rate"],
            row["success_sd_sample"],
            row["mean_tokens"],
            row["mean_wall_time_s"],
        ])

print("PASS: Final summaries generated")
print("CSV:", csv_path)
print("JSON:", json_path)
print("Attempts:", len(records))
print("Verified solves:", summary["overall"]["solved"])
print(
    "Success rate:",
    f'{summary["overall"]["success_rate"] * 100:.2f}%'
)
