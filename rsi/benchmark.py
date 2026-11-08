"""Normalize exact-source paired Chromium evidence; no promotion authority."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median

from rsi.native import generate


def validate(root: Path, evidence: dict) -> dict:
    generated = generate(root)
    if len(generated["candidates"]) != 1:
        raise ValueError("missing exact-source candidate")
    candidate = generated["candidates"][0]
    samples = evidence.get("samples")
    operations = evidence.get("operations_per_sample")
    if (evidence.get("schema") != "axiom-site-rsi/browser-v1"
            or evidence.get("browser") != "chromium"
            or evidence.get("source_revision") != generated["source_revision"]
            or evidence.get("source_sha256") != candidate["source_sha256"]
            or evidence.get("candidate_sha256") != candidate["candidate_sha256"]
            or evidence.get("quality_equivalent") is not True
            or evidence.get("production_representative") is not False
            or evidence.get("promotion_authorized") is not False
            or type(operations) is not int or operations < 1
            or not isinstance(samples, list) or len(samples) < 11):
        raise ValueError("incomplete or unrepresentative browser receipt")
    base, changed = [], []
    for sample in samples:
        if (not isinstance(sample, dict)
                or type(sample.get("baseline_ns_per_op")) not in (float, int)
                or type(sample.get("candidate_ns_per_op")) not in (float, int)
                or not 0 < sample["baseline_ns_per_op"] < 1e12
                or not 0 < sample["candidate_ns_per_op"] < 1e12
                or sample.get("behavior_equivalent") is not True):
            raise ValueError("invalid paired browser sample")
        base.append(sample["baseline_ns_per_op"])
        changed.append(sample["candidate_ns_per_op"])
    baseline = median(base)
    proposed = median(changed)
    gain = (baseline - proposed) * 100 / baseline
    return {"schema": "axiom-native-rsi/benchmark-v1",
            "source_revision": generated["source_revision"],
            "candidate_id": candidate["candidate_id"],
            "source_sha256": candidate["source_sha256"],
            "candidate_sha256": candidate["candidate_sha256"],
            "workload_provenance": "synthetic local Chromium actual DOM theme interactions on representative website routes and viewports, not production field data",
            "paired_samples": len(samples), "operations_per_sample": operations,
            "baseline_median_ns_per_op": baseline,
            "candidate_median_ns_per_op": proposed,
            "gain_percentage": gain,
            "quality_equivalent": True,
            "production_representative": False,
            "independent_implementation_review": False,
            "promotion_authorized": False,
            "status": "POSITIVE_MACHINE_MEASUREMENT" if gain > 0 else "NONPOSITIVE_MEASUREMENT"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = validate(root, json.loads(args.browser_report.read_text()))
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": result["status"],
                      "paired_samples": result["paired_samples"],
                      "promotion_authorized": False}))
