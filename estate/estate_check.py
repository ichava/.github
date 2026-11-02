#!/usr/bin/env python3
"""Estate check for the ichava organisation.

Guards three release decisions that had no executable check (final audit rows X-01, X-03,
X-08, XR-8):

* X-01  no lock file is tracked in any repository (go.sum is Go's checksum file, not a lock,
        and is allowed);
* X-08  demos are local only, so no repository tracks a path under a ``demos/`` directory;
* X-03  the coupled packages move their minor version in lockstep: the latest final ``vX.Y.Z``
        tag of every coupled repository shares one ``X.Y`` (patches stay per repository).

Every non-archived repository of the org is inspected through a shallow, blobless clone of its
default branch (``--depth 1 --filter=blob:none --no-checkout``), which fetches trees and no file
contents, so ``icon-sets-bundled`` and its 121k SVGs cost a tree walk rather than a checkout.
Tags come from ``git ls-remote``.

The check asserts how many repositories it inspected and fails below ``--floor``, so a listing
that silently returns nothing (a token without access, a renamed org) cannot pass as a clean
estate.

``--from-json`` replaces the network with a fixture of the same shape the collector produces,
which is how the tests and a proof-of-failure run exercise the verdict without GitHub.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ORG = "ichava"
DEFAULT_FLOOR = 12

# Lock files by basename, in any directory. go.sum is deliberately absent.
LOCK_FILES = frozenset(
    {
        "package-lock.json",
        "npm-shrinkwrap.json",
        "composer.lock",
        "yarn.lock",
        "pnpm-lock.yaml",
        "bun.lock",
        "bun.lockb",
        "poetry.lock",
        "uv.lock",
        "Pipfile.lock",
        "Gemfile.lock",
        "Cargo.lock",
    }
)

# The packages released together. A minor bump in one is a minor bump in all.
COUPLED = (
    "core",
    "icon-browser",
    "icon-sets-flag",
    "icon-sets-tabler",
    "icon-sets-emoji",
    "icon-sets-bundled",
    "icon-sets-metronic",
    "icon-sets-package-scaffolder",
    "js-ui-kernel",
    "js-motion",
    "react-icon-browser",
    "react-landingpage",
)

FINAL_TAG = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")


# --------------------------------------------------------------------------------------------
# Verdict (pure)
# --------------------------------------------------------------------------------------------


def lock_files(paths: list[str]) -> list[str]:
    return sorted(p for p in paths if p.rsplit("/", 1)[-1] in LOCK_FILES)


def demo_paths(paths: list[str]) -> list[str]:
    return sorted(p for p in paths if "demos" in p.split("/")[:-1])


def latest_final_tag(tags: list[str]) -> tuple[int, int, int] | None:
    versions = []
    for tag in tags:
        m = FINAL_TAG.match(tag)
        if m:
            versions.append(tuple(int(g) for g in m.groups()))
    return max(versions) if versions else None


def evaluate(estate: dict, floor: int) -> tuple[list[str], list[str]]:
    """Return (failures, report lines) for an estate snapshot.

    ``estate`` maps repository name to ``{"paths": [...], "tags": [...]}``.
    """
    failures: list[str] = []
    report: list[str] = []

    inspected = len(estate)
    report.append(f"repositories inspected: {inspected} (floor {floor})")
    if inspected < floor:
        failures.append(f"inspected {inspected} repositories, below the floor of {floor}")

    for name in sorted(estate):
        paths = estate[name]["paths"]
        report.append(f"  {name}: {len(paths)} tracked paths")
        if not paths:
            failures.append(f"{name}: tree listing is empty, so nothing was checked")
        for p in lock_files(paths):
            failures.append(f"X-01 {name}: tracked lock file {p}")
        hits = demo_paths(paths)
        if hits:
            shown = ", ".join(hits[:5]) + (" ..." if len(hits) > 5 else "")
            failures.append(f"X-08 {name}: {len(hits)} tracked path(s) under demos/: {shown}")

    minors: dict[tuple[int, int], list[str]] = {}
    for name in COUPLED:
        if name not in estate:
            failures.append(f"X-03 {name}: coupled repository not found in the org listing")
            continue
        latest = latest_final_tag(estate[name]["tags"])
        if latest is None:
            failures.append(f"X-03 {name}: no final vX.Y.Z tag")
            continue
        report.append(f"  {name}: latest v{latest[0]}.{latest[1]}.{latest[2]}")
        minors.setdefault(latest[:2], []).append(name)
    if len(minors) > 1:
        split = "; ".join(
            f"{major}.{minor}.x: {', '.join(names)}" for (major, minor), names in sorted(minors.items())
        )
        failures.append(f"X-03 coupled packages are not on one minor ({split})")

    return failures, report


# --------------------------------------------------------------------------------------------
# Collector (network)
# --------------------------------------------------------------------------------------------


def run(cmd: list[str], **kwargs) -> str:
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kwargs).stdout


def git_auth_args() -> list[str]:
    token = os.environ.get("GH_TOKEN")
    if not token:
        return []  # rely on the local credential helper
    basic = base64.b64encode(f"x-access-token:{token}".encode()).decode()
    return ["-c", f"http.https://github.com/.extraheader=AUTHORIZATION: basic {basic}"]


def list_repos(org: str) -> list[str]:
    out = run(
        ["gh", "repo", "list", org, "--no-archived", "--limit", "500", "--json", "name,isEmpty"]
    )
    return sorted(r["name"] for r in json.loads(out) if not r["isEmpty"])


def collect(org: str) -> dict:
    estate = {}
    auth = git_auth_args()
    with tempfile.TemporaryDirectory() as scratch:
        for name in list_repos(org):
            url = f"https://github.com/{org}/{name}.git"
            dest = Path(scratch) / name
            run(
                ["git", *auth, "clone", "--quiet", "--depth", "1", "--filter=blob:none",
                 "--no-checkout", url, str(dest)]
            )
            paths = run(["git", "-C", str(dest), "ls-tree", "-r", "--name-only", "HEAD"]).splitlines()
            refs = run(["git", *auth, "ls-remote", "--tags", "--refs", url, "refs/tags/v*"]).splitlines()
            tags = [line.split("refs/tags/", 1)[1] for line in refs if "refs/tags/" in line]
            estate[name] = {"paths": paths, "tags": tags}
    return estate


# --------------------------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--org", default=ORG)
    parser.add_argument("--floor", type=int, default=DEFAULT_FLOOR)
    parser.add_argument("--from-json", type=Path, help="evaluate a fixture instead of the live org")
    parser.add_argument("--dump-json", type=Path, help="write the collected snapshot here")
    args = parser.parse_args(argv)

    if args.from_json:
        estate = json.loads(args.from_json.read_text())
    else:
        estate = collect(args.org)
        if args.dump_json:
            args.dump_json.write_text(json.dumps(estate))

    failures, report = evaluate(estate, args.floor)
    print("\n".join(report))
    if failures:
        print(f"\nFAIL: {len(failures)} finding(s)")
        for f in failures:
            print(f"  {f}")
            if os.environ.get("GITHUB_ACTIONS") == "true":
                print(f"::error title=Estate check::{f}")
        return 1
    print("\nOK: no lock files, no tracked demos/, coupled packages on one minor")
    return 0


if __name__ == "__main__":
    sys.exit(main())
