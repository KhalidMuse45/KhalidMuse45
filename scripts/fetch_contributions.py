"""Scrape the public contribution calendar into data/contrib.json.

Uses github.com/users/<user>/contributions, which needs no token, so the
daily workflow runs with zero secrets.
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

USER = sys.argv[1] if len(sys.argv) > 1 else "KhalidMuse45"
OUT = Path(__file__).resolve().parent.parent / "data" / "contrib.json"


def main():
    req = urllib.request.Request(
        f"https://github.com/users/{USER}/contributions",
        headers={"User-Agent": "profile-art-bot"},
    )
    html = urllib.request.urlopen(req, timeout=30).read().decode()

    cells = {}
    for m in re.finditer(r'<td[^>]*data-date="([\d-]+)"[^>]*id="([^"]+)"[^>]*data-level="(\d)"', html):
        cells[m.group(2)] = {"date": m.group(1), "level": int(m.group(3)), "count": 0}
    for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        n = re.match(r"([\d,]+) contribution", m.group(2).strip())
        if m.group(1) in cells and n:
            cells[m.group(1)]["count"] = int(n.group(1).replace(",", ""))

    if not cells:
        sys.exit("no contribution cells found; GitHub markup may have changed")
    days = sorted(cells.values(), key=lambda d: d["date"])
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"user": USER, "days": days}, indent=1))
    print(f"{len(days)} days, {sum(d['count'] for d in days)} contributions -> {OUT}")


if __name__ == "__main__":
    main()
