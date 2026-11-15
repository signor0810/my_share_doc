#!/usr/bin/env python3
"""Scan a file for likely secrets / private data before publishing to a public repo.

Usage:  python scan_secrets.py <file>
Exit:   0 = nothing suspicious, 2 = findings (printed, matches masked), 1 = usage/IO error.
Standard library only.
"""
import re
import sys

PATTERNS = [
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    ("sk-api-key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")),
    ("vendor-token", re.compile(
        r"\b(?:hf_[A-Za-z0-9]{30,}|gsk_[A-Za-z0-9]{30,}|xai-[A-Za-z0-9]{30,}|glpat-[A-Za-z0-9_-]{20,}"
        r"|npm_[A-Za-z0-9]{36}|\d{8,10}:AA[A-Za-z0-9_-]{33})")),
    ("bearer-token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{20,}=*")),
    ("url-credentials", re.compile(r"[a-z][a-z0-9+.-]*://[^\s/:@\"'<>]+:[^\s/@\"'<>]{3,}@")),
    ("jwt",re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("credential-assignment", re.compile(
        r"(?i)\b(?:api[_-]?key|secret|token|passwd|password|pwd)\b[\"']?\s*[:=]\s*[\"']?[^\s\"'<>,;]{8,}")),
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")),
    # RFC1918 + CGNAT (100.64/10, used by Tailscale); not part of a longer dotted number.
    ("internal-ip", re.compile(
        r"(?<![\d.])(?:10(?:\.\d{1,3}){3}"
        r"|192\.168(?:\.\d{1,3}){2}"
        r"|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}"
        r"|100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])(?:\.\d{1,3}){2})(?![\d.])")),
]

# Placeholder / documentation domains that are not private emails.
SAFE_EMAIL_DOMAINS = ("example.com", "example.org", "example.net", "localhost", "test.com")


def mask(s):
    return s if len(s) <= 6 else s[:4] + "*" * min(len(s) - 4, 8)


def scan_text(text):
    """Return a list of (line_no, category, masked_match)."""
    findings = []
    for no, line in enumerate(text.splitlines(), 1):
        for cat, rx in PATTERNS:
            for m in rx.finditer(line):
                hit = m.group(0)
                if cat == "email" and hit.lower().endswith(SAFE_EMAIL_DOMAINS):
                    continue
                findings.append((no, cat, mask(hit)))
    return findings


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 1
    try:
        with open(argv[1], encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    findings = scan_text(text)
    if not findings:
        print("scan: no suspicious content found")
        return 0
    print(f"scan: {len(findings)} suspicious item(s) in {argv[1]} (matches masked):")
    for no, cat, hit in findings:
        print(f"  line {no}: {cat}: {hit}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
