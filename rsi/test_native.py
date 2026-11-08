"""Adversarial exact-source and normal Git reverse-patch tests."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from rsi.native import GenerationError, generate, propose, validate_rule

ROOT = Path(__file__).resolve().parents[1]
RULE = json.loads((ROOT / "rsi/generators.json").read_text())["rules"][0]
SOURCE = (ROOT / "theme.js").read_text(encoding="utf-8")


class NativeRSITests(unittest.TestCase):
    def test_deterministic_generation_and_no_source_write(self):
        original = (ROOT / "theme.js").read_bytes()
        first = generate(ROOT)
        self.assertEqual(first, generate(ROOT))
        self.assertEqual(first["status"], "GENERATED")
        self.assertEqual(len(first["candidates"]), 1)
        self.assertFalse(first["mutation_authority"])
        self.assertFalse(first["candidates"][0]["mutation_authority"])
        self.assertEqual(first["candidates"][0]["source_sha256"], sha256(original).hexdigest())
        self.assertEqual((ROOT / "theme.js").read_bytes(), original)
        with self.assertRaises(GenerationError):
            generate(ROOT, "0" * 40)

    def test_reject_invalid_target_and_ambiguous_anchor(self):
        with self.assertRaises(GenerationError):
            propose(SOURCE + RULE["before"], RULE, "a" * 40)
        for target in ("../theme.js", "/theme.js", "assets/theme.js",
                       "theme.mjs", "index.html", "styles.css", "rsi/native.py"):
            with self.subTest(target=target), self.assertRaises(GenerationError):
                validate_rule({**RULE, "path": target})
        with self.assertRaises(GenerationError):
            validate_rule({**RULE, "after": RULE["before"]})

    def test_git_apply_reverse_is_lossless(self):
        patch = propose(SOURCE, RULE, "a" * 40)["patch"]
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            file = root / "theme.js"
            file.write_text(SOURCE, encoding="utf-8")
            original = file.read_bytes()
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            for action in (["apply", "--check", "-"], ["apply", "-"],
                           ["apply", "-R", "--check", "-"], ["apply", "-R", "-"]):
                subprocess.run(["git", *action], cwd=root, input=patch, text=True,
                               capture_output=True, check=True)
            self.assertEqual(file.read_bytes(), original)
        applied = SOURCE.replace(RULE["before"], RULE["after"], 1)
        self.assertIsNone(propose(applied, RULE, "a" * 40))


if __name__ == "__main__":
    unittest.main()
