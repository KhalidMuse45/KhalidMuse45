"""Shared look for every generated SVG: GitHub-dark terminal window."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BG, PANEL, BORDER = "#0d1117", "#161b22", "#30363d"
FG, DIM, ACCENT = "#c9d1d9", "#8b949e", "#39d353"
LEVELS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"


def load():
    """Return (user, days) from data/contrib.json."""
    data = json.loads((ROOT / "data" / "contrib.json").read_text())
    return data["user"].lower(), data["days"]


def window(w, h, title, body, style="", title_size=13):
    """Wrap body in a macOS-style terminal window of size w x h."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{MONO}">
<style>{style}text.t{{font-size:{title_size}px}}</style>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<path d="M0.5 36V10.5a10 10 0 0 1 10-10h{w - 21}a10 10 0 0 1 10 10V36z" fill="{PANEL}" stroke="{BORDER}"/>
<circle cx="20" cy="18" r="6" fill="#ff5f56"/><circle cx="40" cy="18" r="6" fill="#ffbd2e"/><circle cx="60" cy="18" r="6" fill="#27c93f"/>
<text class="t" x="{w / 2}" y="24" fill="{DIM}" text-anchor="middle">{title}</text>
{body}
</svg>
"""


def write(name, svg):
    (ROOT / name).write_text(svg)
    print(f"wrote {name}")
