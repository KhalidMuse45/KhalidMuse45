"""Render streak / totals card (stats.svg), sized 840x880 to sit beside the portrait."""
from collections import Counter
from datetime import date

from theme import ACCENT, BORDER, DIM, FG, LEVELS, load, window, write

W, H = 840, 880
WEEKDAYS = ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")


def streaks(days):
    longest = run = 0
    best_end = None
    for d in days:
        run = run + 1 if d["count"] else 0
        if run > longest:
            longest, best_end = run, d["date"]
    # today may still be empty; don't let that break the current streak
    tail = days[:-1] if days[-1]["count"] == 0 else days
    current = 0
    for d in reversed(tail):
        if not d["count"]:
            break
        current += 1
    return current, longest, best_end


def fmt(iso):
    return date.fromisoformat(iso).strftime("%b %-d, %Y")


def plural(n, word):
    return f"{n} {word}{'' if n == 1 else 's'}"


def main():
    user, days = load()
    total = sum(d["count"] for d in days)
    active = sum(1 for d in days if d["count"])
    current, longest, longest_end = streaks(days)
    best = max(days, key=lambda d: d["count"])
    by_wd = Counter()
    for d in days:
        by_wd[date.fromisoformat(d["date"]).strftime("%a")] += d["count"]
    peak = max(by_wd.values()) or 1

    out, y, n = [], 0, 0

    def step():
        nonlocal n
        n += 1
        return f"animation-delay:{0.12 * n:.2f}s"

    def cmd(text):
        out.append(f'<text class="l" style="{step()}" x="40" y="{y}"><tspan fill="{ACCENT}">❯</tspan> <tspan fill="{FG}">{text}</tspan></text>')

    def stat(label, value, note=""):
        out.append(
            f'<g class="l" style="{step()}"><text x="60" y="{y}" fill="{DIM}">{label}</text>'
            f'<line x1="290" y1="{y - 6}" x2="560" y2="{y - 6}" stroke="{BORDER}" stroke-dasharray="2 6"/>'
            f'<text class="big" x="790" y="{y + 4}" text-anchor="end">{value}</text>'
            + (f'<text class="note" x="790" y="{y + 28}" text-anchor="end">{note}</text>' if note else "")
            + "</g>"
        )

    y = 95
    cmd(f"./stats.sh --user {user}")
    y += 62
    for label, value, note in (
        ("total contributions", str(total), "in the last year"),
        ("current streak", plural(current, "day"), ""),
        ("longest streak", plural(longest, "day"), f"ended {fmt(longest_end)}" if longest_end else ""),
        ("best day", str(best["count"]), fmt(best["date"])),
        ("active days", f"{active}/{len(days)}", f"{100 * active / len(days):.0f}% of the year"),
    ):
        stat(label, value, note)
        y += 66

    y += 10
    cmd("./weekdays.sh")
    y += 46
    for wd in WEEKDAYS:
        count, frac = by_wd[wd], by_wd[wd] / peak
        level = 0 if not count else min(4, 1 + int(frac * 3.99))
        delay = step()
        out.append(
            f'<g class="l" style="{delay}"><text x="60" y="{y}" fill="{DIM}">{wd}</text>'
            f'<rect x="130" y="{y - 18}" width="560" height="22" rx="5" fill="{LEVELS[0]}"/>'
            f'<rect class="b" x="130" y="{y - 18}" width="{max(6, 560 * frac):.0f}" height="22" rx="5" fill="{LEVELS[level]}" style="{delay}"/>'
            f'<text x="790" y="{y}" fill="{FG}" text-anchor="end">{count}</text></g>'
        )
        y += 34

    y += 22
    cmd("date")
    y += 32
    out.append(f'<text class="l" style="{step()}" x="60" y="{y}" fill="{DIM}">last updated {fmt(days[-1]["date"])}</text>')
    y += 44
    out.append(f'<text class="l" style="{step()}" x="40" y="{y}" fill="{ACCENT}">❯ <tspan class="cur">█</tspan></text>')

    style = f"""
text{{font-size:20px}}
.big{{font-size:34px;font-weight:bold;fill:{ACCENT}}}
.note{{font-size:15px;fill:{DIM}}}
.l{{opacity:0;animation:in .4s ease-out forwards}}@keyframes in{{from{{opacity:0;transform:translateX(-8px)}}to{{opacity:1;transform:none}}}}
.b{{transform-box:fill-box;transform-origin:left;animation:grow .8s ease-out both}}@keyframes grow{{from{{transform:scaleX(0)}}}}
.cur{{animation:blink 1s step-end infinite}}@keyframes blink{{50%{{opacity:0}}}}
"""
    write("stats.svg", window(W, H, f"{user}@github: ~/stats", "\n".join(out), style, title_size=18))


if __name__ == "__main__":
    main()
