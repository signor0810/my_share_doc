#!/usr/bin/env python3
"""Locate (or clone) the my_share_doc repo and make sure it is safe to publish from.

Usage:  python resolve_repo.py
Prints the repo path on stdout and exits 0. Exits 1 with a message on stderr if unsafe.

Location: $WC_SHARE_REPO, else <home>/my_share_doc. Clones if missing.
Safety (publish.py runs `git add -A` and `git push origin HEAD:main`, so the clone must be
on `main` with a clean working tree, otherwise unrelated files would be published).
Standard library only.
"""
import os
import subprocess
import sys

REMOTE = "https://github.com/signor0810/my_share_doc.git"


def repo_path():
    env = os.environ.get("WC_SHARE_REPO")
    if env:
        return os.path.abspath(os.path.expanduser(env))
    return os.path.join(os.path.expanduser("~"), "my_share_doc")


def git(path, *args):
    return subprocess.run(["git", "-C", path, *args], capture_output=True, text=True)


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    return 1


def main():
    path = repo_path()
    if not os.path.isdir(os.path.join(path, ".git")):
        if os.path.exists(path) and os.listdir(path):
            return fail(f"{path} exists, is not empty, and is not a git clone")
        r = subprocess.run(["git", "clone", REMOTE, path], capture_output=True, text=True)
        if r.returncode:
            return fail("git clone failed:\n" + r.stderr)
    if "my_share_doc" not in git(path, "remote", "get-url", "origin").stdout:
        return fail(f"{path} is not a clone of my_share_doc")
    branch = git(path, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    dirty = git(path, "status", "--porcelain").stdout.strip()
    if dirty:
        return fail(f"{path} has uncommitted changes; publish.py would publish them too:\n{dirty}")
    if branch != "main":
        r = git(path, "checkout", "main")
        if r.returncode:
            return fail(f"cannot switch {path} from '{branch}' to main:\n{r.stderr}")
    if not os.path.isfile(os.path.join(path, "publish.py")):
        return fail(f"publish.py missing in {path}")
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
