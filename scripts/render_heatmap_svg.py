"""Render data/contrib.json as an animated contribution heatmap (contrib-heatmap.svg).

Cells pop in column by column; the animation is pure CSS so it plays inside
GitHub's <img> sandbox.
"""
from datetime import date

from theme import ACCENT, DIM, FG, LEVELS, load, window, write

CELL, GAP = 12, 3
LEFT, TOP = 45, 80


def main():
    user, days = load()
    first = date.fromisoformat(days[0]["date"])
    lead = (first.weekday() + 1) % 7  # GitHub columns start on Sunday

    cols = (len(days) + lead + 6) // 7
    W = LEFT + cols * (CELL + GAP) + 25
    cells, months, last_month = [], [], None
    for i, d in enumerate(days):
        slot = i + lead
        col, row = divmod(slot, 7)
        x, y = LEFT + col * (CELL + GAP), TOP + row * (CELL + GAP)
        delay = col * 0.035 + row * 0.01
        tip = f"{d['count']} contribution{'s' if d['count'] != 1 else ''} on {d['date']}"
        cells.append(
            f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" '
            f'fill="{LEVELS[d["level"]]}" style="animation-delay:{delay:.3f}s"><title>{tip}</title></rect>'
        )
        dt = date.fromisoformat(d["date"])
        if dt.month != last_month and row == 0:
            if x < W - 50:  # skip a label that would run off the right edge
                months.append(f'<text x="{x}" y="{TOP - 10}">{dt.strftime("%b")}</text>')
            last_month = dt.month

    weekdays = "".join(
        f'<text x="{LEFT - 10}" y="{TOP + r * (CELL + GAP) + 10}" text-anchor="end">{n}</text>'
        for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
    )
    total = sum(d["count"] for d in days)
    gy = TOP + 7 * (CELL + GAP) + 30
    legend_x = W - 200
    legend = "".join(
        f'<rect x="{legend_x + 40 + i * 18}" y="{gy - 11}" width="{CELL}" height="{CELL}" rx="3" fill="{c}"/>'
        for i, c in enumerate(LEVELS)
    )
    body = f"""<g fill="{DIM}" font-size="11">{"".join(months)}{weekdays}</g>
<g>{"".join(cells)}</g>
<text x="{LEFT}" y="{gy}" font-size="13" fill="{FG}"><tspan fill="{ACCENT}" font-weight="bold">{total}</tspan> contributions in the last year<tspan class="cur" fill="{ACCENT}"> █</tspan></text>
<g font-size="11" fill="{DIM}"><text x="{legend_x}" y="{gy}">Less</text>{legend}<text x="{legend_x + 40 + 5 * 18 + 4}" y="{gy}">More</text></g>"""
    style = """
.c{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .35s ease-out forwards}
@keyframes pop{0%{opacity:0;transform:scale(.2)}70%{opacity:1;transform:scale(1.25)}100%{opacity:1;transform:scale(1)}}
.cur{animation:blink 1s step-end infinite}@keyframes blink{50%{opacity:0}}
"""
    write("contrib-heatmap.svg", window(W, gy + 25, f"{user}@github: ~/contributions", body, style))


if __name__ == "__main__":
    main()
