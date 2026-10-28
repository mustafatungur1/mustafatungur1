"""contributions.json'dan animasyonlu katkı ısı haritası SVG'si çizer.

Haftalar soldan sağa bir kez açılır, sonra durur.
Kullanım: python scripts/render_heatmap_svg.py data/contributions.json contrib-heatmap.svg
"""
import json
import sys
from datetime import date

WIDTH = 860
CELL = 12
GAP = 3
STEP = CELL + GAP
LEFT = 34
TOP = 52
BG = "#ffffff"
BORDER = "#d0d7de"
DIM = "#656d76"
TEXT = "#1f2328"
ACCENT = "#1f2328"
LEVELS = ["#eff2f5", "#c8ced6", "#8c959f", "#57606a", "#24292f", "#000000"]
MONTHS = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]


def main(src: str, dst: str) -> None:
    data = json.load(open(src, encoding="utf-8"))
    days = data["days"]

    # Haftalara böl (pazar başlangıçlı, GitHub ile aynı)
    weeks, week = [], []
    for d in days:
        wd = (date.fromisoformat(d["date"]).weekday() + 1) % 7
        if wd == 0 and week:
            weeks.append(week)
            week = []
        week.append((wd, d))
    if week:
        weeks.append(week)

    max_count = max((d["count"] for d in days), default=0)
    grid_w = len(weeks) * STEP - GAP
    x0 = LEFT + (WIDTH - LEFT - 14 - grid_w) / 2
    height = TOP + 7 * STEP + 70

    cells, labels = [], []
    last_month, last_label = None, -9
    for i, wk in enumerate(weeks):
        x = x0 + i * STEP
        m = date.fromisoformat(wk[0][1]["date"]).month
        if m != last_month:
            # Yan yana binmesin: önceki etiketten en az 3 hafta sonra
            if i - last_label >= 3 and i < len(weeks) - 2:
                labels.append(f'<text x="{x:.0f}" y="{TOP - 8}">{MONTHS[m - 1]}</text>')
                last_label = i
            last_month = m
        col = []
        for wd, d in wk:
            lvl = d["level"]
            # Çok yoğun günler için ekstra parlak ton
            if max_count and d["count"] >= max_count * 0.85 and d["count"] > 0:
                lvl = 5
            col.append(f'<rect x="{x:.0f}" y="{TOP + wd * STEP}" width="{CELL}" height="{CELL}" rx="2.5" '
                       f'fill="{LEVELS[lvl]}"><title>{d["date"]}: {d["count"]}</title></rect>')
        cells.append(f'<g class="w" style="animation-delay:{0.2 + i * 0.025:.3f}s">{"".join(col)}</g>')

    for wd, name in ((1, "Pzt"), (3, "Çar"), (5, "Cum")):
        labels.append(f'<text x="{x0 - 8:.0f}" y="{TOP + wd * STEP + 10}" text-anchor="end">{name}</text>')

    ly = TOP + 7 * STEP + 26
    legend = "".join(
        f'<rect x="{WIDTH - 150 + n * 16}" y="{ly - 10}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>'
        for n, c in enumerate(LEVELS)
    )
    stats = (
        f'<text x="{x0:.0f}" y="{ly}" fill="{TEXT}">'
        f'<tspan fill="{ACCENT}" font-weight="700">{data["total"]:,}</tspan> katkı'
        f'<tspan fill="{DIM}">  ·  </tspan>güncel seri <tspan fill="{ACCENT}" font-weight="700">{data["current_streak"]}</tspan> gün'
        f'<tspan fill="{DIM}">  ·  </tspan>en uzun <tspan fill="{ACCENT}" font-weight="700">{data["longest_streak"]}</tspan> gün</text>'
    ).replace(",", ".")
    updated = f'<text x="{x0:.0f}" y="{ly + 22}" fill="{DIM}" font-size="11">son güncelleme: {days[-1]["date"]}</text>'

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">\n'
        "<style>"
        ".w{opacity:0;animation:pop .4s ease-out forwards}"
        "@keyframes pop{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:none}}"
        "</style>\n"
        f'<rect x=".5" y=".5" width="{WIDTH - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>\n'
        f'<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="12">\n'
        f'<text x="{x0:.0f}" y="24" fill="{ACCENT}" font-weight="700" font-size="13">GitHub aktivitesi '
        f'<tspan fill="{DIM}" font-weight="400">· son 12 ay</tspan></text>\n'
        f'<g fill="{DIM}" font-size="10.5">{"".join(labels)}</g>\n'
        + "\n".join(cells) + "\n"
        f'{stats}\n{updated}\n'
        f'<text x="{WIDTH - 186}" y="{ly}" fill="{DIM}" font-size="10.5">az</text>{legend}'
        f'<text x="{WIDTH - 150 + len(LEVELS) * 16 + 2}" y="{ly}" fill="{DIM}" font-size="10.5">çok</text>\n'
        "</g>\n</svg>\n"
    )
    with open(dst, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"yazıldı: {dst} ({len(weeks)} hafta)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
