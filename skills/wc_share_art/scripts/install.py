#!/usr/bin/env python3
"""Link this skill (single source in the repo) into each installed agent's skill directory.

Usage:  python install.py [--dry-run]
Windows: directory junction (no admin needed). Linux/macOS: symlink.
Never overwrites an existing path that is not already a link to this skill.
An agent is installed only if its config directory already exists. Standard library only.
"""
import os
import subprocess
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "wc_share_art"
HOME = os.path.expanduser("~")
PI_DIR = os.environ.get("PI_CODING_AGENT_DIR") or os.path.join(HOME, ".pi", "agent")


def candidates():
    """(agent, skills_dir, marker_dir) -- install only when marker_dir exists."""
    claude = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(HOME, ".claude")
    hermes = os.environ.get("HERMES_HOME") or os.path.join(HOME, ".hermes")
    return [
        ("claude", os.path.join(claude, "skills"), claude),
        ("pi", os.path.join(PI_DIR, "skills"), PI_DIR),
        ("hermes", os.path.join(hermes, "skills"), hermes),
        ("agy", os.path.join(HOME, ".gemini", "config", "skills"), os.path.join(HOME, ".gemini", "config")),
        ("codex", os.path.join(HOME, ".codex", "skills"), os.path.join(HOME, ".codex")),
    ]


def is_link(path):
    if os.path.islink(path):
        return True
    return os.name == "nt" and os.path.isdir(path) and bool(
        os.lstat(path).st_file_attributes & 0x400)  # FILE_ATTRIBUTE_REPARSE_POINT


def make_link(link, target):
    if os.name == "nt":
        r = subprocess.run(["cmd", "/c", "mklink", "/J", link, target], capture_output=True, text=True)
        if r.returncode:
            raise OSError(r.stderr or r.stdout)
    else:
        os.symlink(target, link, target_is_directory=True)


def render_pi_prompt(dry):
    src = os.path.join(SKILL_DIR, "agents", "pi-prompt.md")
    prompts = os.path.join(PI_DIR, "prompts")
    dest = os.path.join(prompts, NAME + ".md")
    skill_md = os.path.join(PI_DIR, "skills", NAME, "SKILL.md").replace("\\", "/")
    text = open(src, encoding="utf-8").read().replace("{{SKILL_MD}}", skill_md)
    if os.path.exists(dest) and open(dest, encoding="utf-8").read() == text:
        return "pi prompt template: up to date"
    if not dry:
        os.makedirs(prompts, exist_ok=True)
        with open(dest, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    return f"pi prompt template: {'would write' if dry else 'written'} {dest}"


def main():
    dry = "--dry-run" in sys.argv
    for agent, skills, marker in candidates():
        link = os.path.join(skills, NAME)
        if not os.path.isdir(marker):
            print(f"{agent}: SKIP (not installed: {marker} missing)")
            continue
        if os.path.lexists(link):
            same = is_link(link) and os.path.realpath(link) == os.path.realpath(SKILL_DIR)
            print(f"{agent}: {'ok (already linked)' if same else 'CONFLICT: exists and is not a link to this skill'} -> {link}")
            continue
        if not dry:
            os.makedirs(skills, exist_ok=True)
            make_link(link, SKILL_DIR)
        print(f"{agent}: {'would link' if dry else 'linked'} {link} -> {SKILL_DIR}")
    if os.path.isdir(PI_DIR):
        print(render_pi_prompt(dry))


if __name__ == "__main__":
    main()
