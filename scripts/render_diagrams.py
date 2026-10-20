#!/usr/bin/env python3
"""Render notebooks/diagrams/*.mmd to PNG for the notebook Markdown cells.

Snowflake Notebook Markdown cells do not render Mermaid, so the notebooks
show these PNGs from the public GitHub repo instead. Edit the .mmd source,
run this script, then commit and push the PNGs.

Requires the Mermaid CLI (`npm install -g @mermaid-js/mermaid-cli`).
Uses the local Google Chrome if present; set CHROME_PATH to override.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

DIAGRAMS = Path(__file__).resolve().parent.parent / "notebooks" / "diagrams"
CONFIG = DIAGRAMS / "mermaid_config.json"
DEFAULT_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def main() -> int:
    cmd_base = ["mmdc", "-c", str(CONFIG), "-b", "white", "-w", "1400", "-s", "2"]
    chrome = os.environ.get("CHROME_PATH", DEFAULT_CHROME)
    if Path(chrome).exists():
        pptr = Path(tempfile.gettempdir()) / "dq_hol_puppeteer.json"
        pptr.write_text(json.dumps({"executablePath": chrome, "headless": "new"}))
        cmd_base += ["-p", str(pptr)]

    failed = 0
    for src in sorted(DIAGRAMS.glob("*.mmd")):
        out = src.with_suffix(".png")
        result = subprocess.run(cmd_base + ["-i", str(src), "-o", str(out)],
                                capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  OK  {out.name}")
        else:
            failed += 1
            print(f"  FAIL {src.name}\n{result.stderr.strip()}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
