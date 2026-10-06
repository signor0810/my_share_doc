# How to share an HTML document (for any AI agent)

This repo is served by GitHub Pages at https://signor0810.github.io/my_share_doc/ .
Anything in `artifacts/` is public and viewable in a browser without login.

## Publish a file

1. Make sure this repo is cloned and you can push to `main`
   (`git clone https://github.com/signor0810/my_share_doc`).
2. Run:

   ```
   python publish.py path/to/file.html [--name my-slug]
   ```

3. The script copies the file to `artifacts/<slug>.html`, regenerates `index.html`,
   commits, pushes to `main`, and prints the public URL. Give that URL to the user.
   It goes live in 1-3 minutes.

## Rules

- Single self-contained `.html` only (inline CSS/JS, no relative asset links).
- Re-publishing the same slug overwrites the earlier version.
- Never publish secrets, credentials, or private data: the repo is public.
- Do not edit `index.html` by hand; `publish.py` regenerates it.
