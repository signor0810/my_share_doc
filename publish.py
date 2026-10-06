#!/usr/bin/env python3
"""Publish an HTML file to this repo's GitHub Pages site and print its public URL.

Usage:  python publish.py <file.html> [--name my-slug] [--no-push]

Copies the file to artifacts/<slug>.html, regenerates index.html, commits,
pushes to main, and prints the share link. Standard library only.
"""
import argparse, glob, hashlib, html, os, re, shutil, subprocess, sys

BASE = "https://signor0810.github.io/my_share_doc/"
ROOT = os.path.dirname(os.path.abspath(__file__))


def title_of(path):
    m = re.search(r"<title>([^<]*)", open(path, encoding="utf8", errors="replace").read(), re.I)
    return html.unescape(m.group(1)).strip() if m else os.path.splitext(os.path.basename(path))[0]


def slugify(src, title):
    stem = os.path.splitext(os.path.basename(src))[0]
    if stem.lower() != "index":
        s = re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")
        if s:
            return s
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s or "doc-" + hashlib.sha1(title.encode()).hexdigest()[:8]


def build_index():
    rows = sorted((title_of(f), os.path.relpath(f, ROOT).replace(os.sep, "/"))
                  for f in glob.glob(os.path.join(ROOT, "artifacts", "*.html")))
    items = "\n".join(f'<li><a href="{f}">{html.escape(t)}</a></li>' for t, f in rows)
    page = f"""<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>my_share_doc</title>
<style>
:root{{--bg:#faf9f5;--fg:#141413;--ac:#12697a;--bd:#dcd9cf}}
@media(prefers-color-scheme:dark){{:root{{--bg:#141413;--fg:#ece9e0;--ac:#57b8c8;--bd:#34332f}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.7 -apple-system,BlinkMacSystemFont,"PingFang TC","Noto Sans TC",sans-serif}}
main{{max-width:760px;margin:0 auto;padding:32px 16px 64px}}
h1{{margin:0 0 4px}}p{{opacity:.7;margin:0 0 24px}}
ul{{list-style:none;padding:0;margin:0}}li{{border-bottom:1px solid var(--bd)}}
a{{display:block;padding:12px 4px;color:var(--ac);text-decoration:none}}a:hover{{text-decoration:underline}}
</style></head><body><main>
<h1>my_share_doc</h1><p>{len(rows)} 份文件</p>
<ul>
{items}
</ul></main></body></html>
"""
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf8").write(page)


def git(*a, check=True):
    return subprocess.run(["git", "-C", ROOT, *a], check=check, capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--name", help="URL slug (default: from filename/title)")
    ap.add_argument("--no-push", action="store_true")
    a = ap.parse_args()
    if not os.path.isfile(a.file) or not a.file.lower().endswith((".html", ".htm")):
        sys.exit("error: need an existing .html file")
    title = title_of(a.file)
    slug = re.sub(r"[^a-z0-9-]+", "-", (a.name or slugify(a.file, title)).lower()).strip("-")
    dest = os.path.join(ROOT, "artifacts", slug + ".html")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if not a.no_push:
        git("pull", "--rebase", "origin", "main", check=False)
    shutil.copyfile(a.file, dest)
    build_index()
    git("add", "-A")
    if git("diff", "--cached", "--quiet", check=False).returncode:
        git("commit", "-m", f"Publish {slug}: {title}")
    if not a.no_push:
        r = git("push", "origin", "HEAD:main", check=False)
        if r.returncode:
            sys.exit("push failed:\n" + r.stderr)
    print(f"{BASE}artifacts/{slug}.html")


if __name__ == "__main__":
    main()
