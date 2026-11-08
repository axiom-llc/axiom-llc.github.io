"""Deterministic, source-bound website RSI proposal; no source writes."""
from __future__ import annotations

import argparse
from difflib import unified_diff
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess

REPO = "axiom-llc/axiom-llc.github.io"
REV = re.compile(r"^[0-9a-f]{40}$")


class GenerationError(ValueError):
    pass


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True)
    if result.returncode:
        raise GenerationError("immutable repository revision unavailable")
    return result.stdout.strip()


def validate_rule(rule: dict) -> None:
    if not isinstance(rule, dict) or set(rule) != {
            "id", "path", "before", "after", "benchmark", "tests"}:
        raise GenerationError("invalid generator schema")
    if (rule["id"] != "theme-label-query-cache" or rule["path"] != "theme.js"
            or rule["benchmark"] != "rsi/benchmark.py"
            or rule["tests"] != ["rsi/test_native.py"]):
        raise GenerationError("unapproved candidate scope")
    a, b = rule["before"], rule["after"]
    if (not isinstance(a, str) or not isinstance(b, str)
            or not 4 <= len(a) <= 4096 or len(b) > 8192
            or a == b or "\0" in a + b):
        raise GenerationError("unsafe source replacement")


def propose(source: str, rule: dict, revision: str) -> dict | None:
    validate_rule(rule)
    if not isinstance(revision, str) or not REV.fullmatch(revision):
        raise GenerationError("stale or unpinned revision")
    count = source.count(rule["before"])
    if count == 0:
        return None
    if count != 1:
        raise GenerationError("ambiguous source anchor")
    candidate = source.replace(rule["before"], rule["after"], 1)
    patch = "".join(unified_diff(source.splitlines(keepends=True),
              candidate.splitlines(keepends=True), fromfile="a/theme.js",
              tofile="b/theme.js", n=3))
    if not patch or len(patch) > 65536:
        raise GenerationError("unsafe generated patch")
    identity = sha256((REPO + "\0" + rule["id"] + "\0" + rule["path"]).encode()).hexdigest()[:20]
    return {"candidate_id": "rsi-" + identity, "repository": REPO,
            "source_revision": revision, "source_path": "theme.js",
            "source_sha256": sha256(source.encode()).hexdigest(),
            "candidate_sha256": sha256(candidate.encode()).hexdigest(),
            "patch_sha256": sha256(patch.encode()).hexdigest(),
            "patch": patch, "benchmark": rule["benchmark"],
            "tests": rule["tests"], "evaluation": "INDEPENDENT_BENCHMARK_REQUIRED",
            "mutation_authority": False}


def generate(root: Path, expected_revision: str | None = None) -> dict:
    root = root.resolve()
    revision = git(root, "rev-parse", "HEAD")
    if (not REV.fullmatch(revision)
            or (expected_revision is not None and expected_revision != revision)
            or git(root, "rev-parse", "--show-toplevel") != str(root)):
        raise GenerationError("source revision mismatch")
    if git(root, "diff", "--name-only", "HEAD", "--", "theme.js"):
        raise GenerationError("modified theme source")
    registry = json.loads((root / "rsi/generators.json").read_text(encoding="utf-8"))
    if (not isinstance(registry, dict)
            or set(registry) != {"schema", "repository", "rules"}
            or registry["schema"] != "axiom-native-rsi/v1"
            or registry["repository"] != REPO
            or not isinstance(registry["rules"], list)
            or len(registry["rules"]) != 1):
        raise GenerationError("untrusted registry")
    rule = registry["rules"][0]
    validate_rule(rule)
    target = root / "theme.js"
    if target.is_symlink() or not target.is_file() or target.stat().st_size > 100000:
        raise GenerationError("invalid source file")
    candidate = propose(target.read_text(encoding="utf-8"), rule, revision)
    return {"schema": "axiom-native-rsi/v1", "repository": REPO,
            "source_revision": revision,
            "status": "GENERATED" if candidate else "NO_APPLICABLE_RULE",
            "candidates": [candidate] if candidate else [],
            "mutation_authority": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--revision")
    args = parser.parse_args()
    result = generate(Path(__file__).resolve().parents[1], args.revision)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "count": len(result["candidates"]),
                      "mutation_authority": False}))
