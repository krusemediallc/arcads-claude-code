"""Regression guards for the money and safety gates.

These exist because the gates they protect were once prose-only: the generators
billed on invocation, and ad creation could be flipped to a spending status by a
one-word change. Every test here is offline and stdlib-only -- no credentials, no
network, no third-party packages -- so CI can run them on every push.

Run:  python -m unittest discover -s tests -p 'test_*.py'
"""

import ast
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GENERATORS = [
    ROOT / "skills" / "chatgpt-image-ad" / "scripts" / "generate_image.py",
    ROOT / "skills" / "nano-banana-image-ad" / "scripts" / "generate_image.py",
]
META_LIB = ROOT / "shared" / "skills" / "meta-ad-builder" / "scripts" / "lib" / "meta_api.py"
DEPLOY_AD = ROOT / "shared" / "skills" / "meta-ad-builder" / "scripts" / "deploy-ad.py"
META_SCRIPTS = (ROOT / "shared" / "skills" / "meta-ad-builder" / "scripts").rglob("*.py")


def run_generator(script, extra, env_file):
    """Invoke a generator offline. --product-id avoids the product lookup call."""
    cmd = [
        sys.executable, str(script),
        "--prompt", "regression guard",
        "--aspect-ratio", "1:1",
        "--product-id", "guard-product",
        "--env-file", str(env_file),
    ] + extra
    return subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=str(ROOT))


class SpendGateTests(unittest.TestCase):
    """The generators must not bill without an explicit confirmation."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.env_file = Path(cls._tmp.name) / "guard.env"
        # Syntactically valid but useless credential: if any test ever reaches the
        # network, it fails rather than spending someone's credits.
        cls.env_file.write_text(
            "ARCADS_BASIC_AUTH='Basic Z3VhcmQ6Z3VhcmQ='\nPRODUCT_ID=guard-product\n",
            encoding="utf-8",
        )

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_refuses_to_spend_without_confirm(self):
        for script in GENERATORS:
            with self.subTest(script=script.parent.parent.name):
                proc = run_generator(script, [], self.env_file)
                self.assertEqual(proc.returncode, 2, proc.stderr)
                self.assertIn("refusing to spend", proc.stderr)

    def test_dry_run_prints_payload_and_exits_clean(self):
        for script in GENERATORS:
            with self.subTest(script=script.parent.parent.name):
                proc = run_generator(script, ["--dry-run"], self.env_file)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn("no billable call made", proc.stderr)
                body = json.loads(proc.stdout)
                self.assertIn("model", body)
                self.assertIn("prompt", body)

    def test_billable_count_is_announced(self):
        proc = run_generator(GENERATORS[0], ["--dry-run", "--n", "4"], self.env_file)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("BILLABLE: 4", proc.stderr)

    def test_confirm_and_dry_run_flags_exist(self):
        for script in GENERATORS:
            with self.subTest(script=script.parent.parent.name):
                tree = ast.parse(script.read_text(encoding="utf-8"))
                flags = {
                    node.args[0].value
                    for node in ast.walk(tree)
                    if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "add_argument"
                    and node.args
                    and isinstance(node.args[0], ast.Constant)
                }
                self.assertIn("--confirm", flags)
                self.assertIn("--dry-run", flags)


class MetaSafetyTests(unittest.TestCase):
    """Ads must stay PAUSED and tokens must stay out of URLs."""

    def _func(self, path, name):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == name:
                return node
        self.fail(f"{name} not found in {path}")

    def test_create_ad_defaults_to_paused(self):
        fn = self._func(META_LIB, "create_ad")
        defaults = dict(
            zip([a.arg for a in fn.args.args][-len(fn.args.defaults):], fn.args.defaults)
        )
        self.assertIn("status", defaults)
        self.assertEqual(defaults["status"].value, "PAUSED")

    def test_deploy_ad_never_overrides_status(self):
        tree = ast.parse(DEPLOY_AD.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "create_ad"):
                passed = {kw.arg for kw in node.keywords}
                self.assertNotIn(
                    "status", passed,
                    "deploy-ad.py must not pass status= to create_ad; PAUSED is the only safe default",
                )

    def test_deploy_ad_has_no_active_flag(self):
        source = DEPLOY_AD.read_text(encoding="utf-8")
        self.assertNotIn("--active", source)
        self.assertIn("--dry-run", source)

    def test_create_ad_does_not_auto_retry(self):
        """Ad creation has no idempotency key, so a retry loop would duplicate ads."""
        fn = self._func(META_LIB, "create_ad")
        loops = [n for n in ast.walk(fn) if isinstance(n, (ast.For, ast.While))]
        self.assertEqual(loops, [], "create_ad must not loop over attempts")

    def test_token_never_sent_as_a_query_or_form_field(self):
        offenders = []
        for path in META_SCRIPTS:
            text = path.read_text(encoding="utf-8")
            for lineno, line in enumerate(text.splitlines(), 1):
                if '"access_token":' in line or "'access_token':" in line:
                    offenders.append(f"{path.relative_to(ROOT)}:{lineno}")
        self.assertEqual(
            offenders, [],
            "pass the Meta token in an Authorization: Bearer header, not a query/form field: "
            + ", ".join(offenders),
        )

    def test_every_graph_request_has_a_timeout(self):
        missing = []
        for path in [META_LIB]:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                        and node.func.attr in {"get", "post"}
                        and isinstance(node.func.value, ast.Name)
                        and node.func.value.id == "requests"):
                    if "timeout" not in {kw.arg for kw in node.keywords}:
                        missing.append(f"{path.name}:{node.lineno}")
        self.assertEqual(missing, [], "requests call without timeout=: " + ", ".join(missing))


class ApiLogTests(unittest.TestCase):
    """The generators must log their own calls, without leaking prompt or credentials."""

    def test_log_flags_exist(self):
        for script in GENERATORS:
            with self.subTest(script=script.parent.parent.name):
                source = script.read_text(encoding="utf-8")
                self.assertIn("--log-file", source)
                self.assertIn("--no-log", source)

    def test_failed_call_is_logged_without_prompt_or_credentials(self):
        """Points at a closed port: exercises the logging path with no real call."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            env_file = tmp / "guard.env"
            env_file.write_text("ARCADS_BASIC_AUTH='Basic Z3VhcmQ6Z3VhcmQ='\n", encoding="utf-8")
            log_file = tmp / "logs" / "arcads-api.jsonl"
            log_file.parent.mkdir()
            secret_words = "canary phrase that must not be logged"
            proc = subprocess.run(
                [sys.executable, str(GENERATORS[0]),
                 "--prompt", secret_words, "--aspect-ratio", "1:1", "--confirm",
                 "--product-id", "guard-product", "--env-file", str(env_file),
                 "--base-url", "http://127.0.0.1:1",
                 "--out", str(tmp / "out"), "--log-file", str(log_file)],
                capture_output=True, text=True, timeout=180, cwd=str(ROOT),
            )
            self.assertEqual(proc.returncode, 1, proc.stderr)  # all variants failed
            self.assertTrue(log_file.exists(), "generator did not write its log")
            blob = log_file.read_text(encoding="utf-8")
            records = [json.loads(line) for line in blob.splitlines() if line.strip()]
            self.assertEqual(len(records), 1)
            rec = records[0]
            self.assertEqual(rec["response"]["status"], "failed")
            self.assertIsNotNone(rec["response"]["error"])
            self.assertEqual(rec["request"]["promptWordCount"], len(secret_words.split()))
            # logs/README.md forbids prompt text and credentials in this file.
            self.assertNotIn("canary phrase", blob)
            self.assertNotIn("Authorization", blob)
            self.assertNotIn("Basic ", blob)

    def test_log_is_skipped_when_directory_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            env_file = tmp / "guard.env"
            env_file.write_text("ARCADS_BASIC_AUTH='Basic Z3VhcmQ6Z3VhcmQ='\n", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(GENERATORS[0]),
                 "--prompt", "x", "--aspect-ratio", "1:1", "--dry-run",
                 "--product-id", "guard-product", "--env-file", str(env_file),
                 "--log-file", str(tmp / "absent" / "deeper" / "x.jsonl")],
                capture_output=True, text=True, timeout=120, cwd=str(ROOT),
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("skipping API logging", proc.stderr)


class ConsentGateTests(unittest.TestCase):
    """The likeness flow must ask before reproducing a real person."""

    def test_likeness_gate_present_in_skill_and_prompt_library(self):
        skill = (ROOT / "skills" / "arcads-external-api" / "SKILL.md").read_text(encoding="utf-8")
        recreate = (ROOT / "skills" / "arcads-external-api" / "prompting"
                    / "prompt-library" / "influencer-recreation.md").read_text(encoding="utf-8")
        for name, text in (("SKILL.md", skill), ("influencer-recreation.md", recreate)):
            with self.subTest(doc=name):
                self.assertIn("permission", text.lower())
                self.assertIn("likeness", text.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
