"""Tests for estate/estate_check.py: each guard must be able to fail, and a clean estate passes."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import estate_check as ec  # noqa: E402


def clean_estate(extra: int = 2) -> dict:
    estate = {
        name: {"paths": ["README.md", "src/a.php"], "tags": ["v0.1.0", "v0.1.3", "v0.2.0-rc.1"]}
        for name in ec.COUPLED
    }
    for i in range(extra):
        estate[f"other-{i}"] = {"paths": ["README.md", "src/go.sum"], "tags": []}
    return estate


class VerdictTest(unittest.TestCase):
    def test_clean_estate_passes(self):
        failures, _ = ec.evaluate(clean_estate(), floor=12)
        self.assertEqual(failures, [])

    def test_go_sum_is_allowed(self):
        self.assertEqual(ec.lock_files(["go.sum", "src/go.sum"]), [])

    def test_lock_file_at_any_depth_fails(self):
        estate = clean_estate()
        estate["core"]["paths"] += ["composer.lock", "resources/js/package-lock.json"]
        failures, _ = ec.evaluate(estate, floor=12)
        self.assertEqual(
            failures,
            ["X-01 core: tracked lock file composer.lock",
             "X-01 core: tracked lock file resources/js/package-lock.json"],
        )

    def test_every_listed_lock_name_is_caught(self):
        paths = [f"x/{name}" for name in sorted(ec.LOCK_FILES)]
        self.assertEqual(len(ec.lock_files(paths)), len(ec.LOCK_FILES))

    def test_tracked_demo_path_fails(self):
        estate = clean_estate()
        estate["other-0"]["paths"] += ["demos/ichava-app/composer.json", "packages/demos/x.txt"]
        failures, _ = ec.evaluate(estate, floor=12)
        self.assertEqual(len(failures), 1)
        self.assertTrue(failures[0].startswith("X-08 other-0: 2 tracked path(s) under demos/"))

    def test_a_file_named_demos_is_not_a_directory(self):
        self.assertEqual(ec.demo_paths(["docs/demos", "demos.md"]), [])

    def test_minor_split_fails(self):
        estate = clean_estate()
        estate["js-motion"]["tags"].append("v0.2.0")
        failures, _ = ec.evaluate(estate, floor=12)
        self.assertEqual(len(failures), 1)
        self.assertIn("X-03 coupled packages are not on one minor", failures[0])
        self.assertIn("0.2.x: js-motion", failures[0])

    def test_patch_drift_is_allowed(self):
        estate = clean_estate()
        estate["core"]["tags"] = ["v0.1.9"]
        self.assertEqual(ec.evaluate(estate, floor=12)[0], [])

    def test_prerelease_and_src_tags_are_ignored(self):
        self.assertEqual(ec.latest_final_tag(["v0.1.2", "v0.2.0-rc.1", "src/v0.3.0"]), (0, 1, 2))

    def test_missing_coupled_repo_fails(self):
        estate = clean_estate()
        del estate["react-landingpage"]
        failures, _ = ec.evaluate(estate, floor=12)
        self.assertIn("X-03 react-landingpage: coupled repository not found in the org listing", failures)

    def test_untagged_coupled_repo_fails(self):
        estate = clean_estate()
        estate["core"]["tags"] = []
        self.assertIn("X-03 core: no final vX.Y.Z tag", ec.evaluate(estate, floor=12)[0])

    def test_below_floor_fails(self):
        failures, _ = ec.evaluate(clean_estate(), floor=99)
        self.assertIn("inspected 14 repositories, below the floor of 99", failures)

    def test_empty_tree_fails(self):
        estate = clean_estate()
        estate["other-1"]["paths"] = []
        self.assertIn("other-1: tree listing is empty, so nothing was checked", ec.evaluate(estate, floor=12)[0])


class CliTest(unittest.TestCase):
    def run_fixture(self, estate: dict) -> int:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "estate.json"
            path.write_text(json.dumps(estate))
            return ec.main(["--from-json", str(path)])

    def test_exit_zero_on_clean(self):
        self.assertEqual(self.run_fixture(clean_estate()), 0)

    def test_exit_one_on_drift(self):
        estate = clean_estate()
        estate["core"]["paths"].append("yarn.lock")
        self.assertEqual(self.run_fixture(estate), 1)


if __name__ == "__main__":
    unittest.main()
