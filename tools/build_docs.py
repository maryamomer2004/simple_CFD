#!/usr/bin/env python3
"""Build the documents of every course problem.

For each folder in ``problems/`` this script

1. runs the Jupyter notebook, so the committed notebook shows its outputs;
2. copies the figures of cells tagged ``fig:<name>`` to ``docs/figures/<name>.png``;
3. turns ``docs/problem.md`` and ``docs/solution.md`` into
   ``01_problem_statement.pdf`` and ``02_solution.pdf``, and, where it exists,
   ``docs/whiteboard.md`` (the instructor's hand-calculation guide) into
   ``04_whiteboard_guide.pdf``.

Inside the Markdown sources, ``{{code:<name>}}`` is replaced by the code of the
notebook cells tagged ``code:<name>`` and ``{{out:<name>}}`` by the printed
output of the cells tagged ``out:<name>``, so the PDFs always show exactly the
code and the numbers of the notebook.

Requirements: pandoc, Google Chrome or Chromium, and ``pip install nbclient ipykernel``.

Usage (from the repository root)::

    python tools/build_docs.py                    # all problems
    python tools/build_docs.py 01_cooling_fin     # one problem
    python tools/build_docs.py --no-run           # reuse the saved notebook outputs
"""

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
PROBLEMS = ROOT / "problems"
MATHJAX_CDN = "https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js"
OUTPUTS = {"problem.md": "01_problem_statement.pdf", "solution.md": "02_solution.pdf",
           "whiteboard.md": "04_whiteboard_guide.pdf"}


def find_chrome(explicit):
    candidates = [explicit, os.environ.get("CHROME")] + [
        shutil.which(name) for name in ("google-chrome", "google-chrome-stable", "chromium",
                                        "chromium-browser", "chrome")]
    candidates += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                   r"C:\Program Files\Google\Chrome\Application\chrome.exe"]
    for c in candidates:
        if c and Path(c).exists():
            return c
    sys.exit("Chrome/Chromium not found: pass --chrome PATH or set $CHROME")


def run_notebook(path):
    import nbformat
    from nbclient import NotebookClient

    nb = nbformat.read(path, as_version=4)
    NotebookClient(nb, timeout=900, kernel_name="python3", record_timing=False,
                   resources={"metadata": {"path": str(path.parent)}}).execute()
    nbformat.write(nb, path)


def tags(cell):
    return cell.get("metadata", {}).get("tags", [])


def harvest(path, figure_dir):
    """Collect tagged code, printed output and figures from a notebook."""
    nb = json.loads(path.read_text(encoding="utf-8"))
    code, out = {}, {}
    figure_dir.mkdir(parents=True, exist_ok=True)
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"]).strip("\n")
        for tag in tags(cell):
            kind, _, name = tag.partition(":")
            if kind == "code":
                code[name] = code[name] + "\n\n" + source if name in code else source
            elif kind == "out":
                text = "".join("".join(o.get("text", "")) for o in cell.get("outputs", [])
                               if o.get("output_type") == "stream" and o.get("name") == "stdout")
                out[name] = out.get(name, "") + text.rstrip("\n")
            elif kind == "fig":
                images = [o["data"]["image/png"] for o in cell.get("outputs", [])
                          if "image/png" in o.get("data", {})]
                if images:
                    data = images[-1]
                    data = "".join(data) if isinstance(data, list) else data
                    (figure_dir / f"{name}.png").write_bytes(base64.b64decode(data))
    return code, out


def expand(markdown, code, out):
    def sub(match):
        kind, name = match.group(1), match.group(2)
        table = code if kind == "code" else out
        if name not in table:
            sys.exit(f"  missing notebook cell tagged '{kind}:{name}'")
        lang = "python" if kind == "code" else "text"
        return f"```{lang}\n{table[name]}\n```"
    return re.sub(r"\{\{(code|out):([\w-]+)\}\}", sub, markdown)


def make_pdf(md_path, pdf_path, code, out, chrome, mathjax):
    docs = md_path.parent
    style = (TOOLS / "doc_style.css").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "header.html").write_text(f"<style>\n{style}\n</style>\n", encoding="utf-8")
        src = tmp / "source.md"
        src.write_text(expand(md_path.read_text(encoding="utf-8"), code, out), encoding="utf-8")
        html = docs / f".{md_path.stem}.html"  # next to the figures, so relative paths work
        subprocess.run(["pandoc", str(src), "--from", "markdown+tex_math_dollars+pipe_tables",
                        "--to", "html5", "--standalone", "--template", str(TOOLS / "doc_template.html"),
                        "--include-in-header", str(tmp / "header.html"), f"--mathjax={mathjax}",
                        "--highlight-style", "tango", "--output", str(html)], check=True)
        try:
            subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
                            "--no-pdf-header-footer", "--virtual-time-budget=60000",
                            f"--print-to-pdf={pdf_path}", html.as_uri()],
                           check=True, capture_output=True)
        finally:
            html.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("problems", nargs="*", help="problem folder names (default: all)")
    parser.add_argument("--chrome", help="Chrome/Chromium executable")
    parser.add_argument("--mathjax", default=MATHJAX_CDN, help="URL or path of MathJax tex-svg.js")
    parser.add_argument("--no-run", action="store_true", help="do not re-execute the notebooks")
    args = parser.parse_args()

    chrome = find_chrome(args.chrome)
    mathjax = args.mathjax if "://" in args.mathjax else Path(args.mathjax).resolve().as_uri()
    folders = [PROBLEMS / p for p in args.problems] if args.problems else sorted(
        p for p in PROBLEMS.iterdir() if p.is_dir() and (p / "docs").is_dir())
    for folder in folders:
        print(folder.name)
        notebook = next(folder.glob("*.ipynb"))
        if not args.no_run:
            print(f"  running   {notebook.name}")
            run_notebook(notebook)
        code, out = harvest(notebook, folder / "docs" / "figures")
        for md_name, pdf_name in OUTPUTS.items():
            md = folder / "docs" / md_name
            if md.exists():
                print(f"  building  {pdf_name}")
                make_pdf(md, folder / pdf_name, code, out, chrome, mathjax)


if __name__ == "__main__":
    main()
