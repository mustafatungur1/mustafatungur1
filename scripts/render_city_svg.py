"""contributions.json'dan izometrik "katkı şehri" SVG'si çizer.

Her gün ışıksız bir prizma: üst yüz beyaz, sol yan saf siyah, sağ yan taralı. Katkısız gün tel
çerçeve karo ("henüz yok"). Bloklar haftaya göre sırayla zeminden yükselir; en yoğun gün en sonda
turuncuya döner ve aynı kavram yazıda da turuncudur.
Kullanım: python scripts/render_city_svg.py data/contributions.json contrib-city.svg
"""
import json
import math
import sys
from datetime import date

import kerem as K

H = 480
U = 12.6                                   # hücre kenarı (px, zemin düzleminde)
A = (U * math.cos(math.radians(20)), -U * math.sin(math.radians(20)))   # hafta ekseni: sağa-yukarı
B = (U * 0.62, U * 0.50)                   # gün ekseni: sağa-aşağı
ORIGIN = (150, 392)
GAP = 0.2                                 # hücre içi boşluk (hücre oranı)
H_MIN, H_MAX = 4, 84
MONTHS = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]


def P(w: float, d: float, h: float = 0) -> tuple[float, float]:
    return ORIGIN[0] + w * A[0] + d * B[0], ORIGIN[1] + w * A[1] + d * B[1] - h


def prism(w: int, d: int, h: float, top: str, edge: str, hatch: str) -> str:
    a, b = w + GAP, w + 1 - GAP
    c, e = d + GAP, d + 1 - GAP
    p00, p10, p01, p11 = P(a, c), P(b, c), P(a, e), P(b, e)
    t00, t10, t01, t11 = P(a, c, h), P(b, c, h), P(a, e, h), P(b, e, h)
    sw = 0.9
    return (f'<polygon points="{K.pts(p00, p01, t01, t00)}" fill="#000" stroke="{edge}" stroke-width="{sw}" stroke-linejoin="round"/>'
            f'<polygon points="{K.pts(p01, p11, t11, t01)}" fill="url(#{hatch})" stroke="{edge}" stroke-width="{sw}" stroke-linejoin="round"/>'
            f'<polygon points="{K.pts(t00, t10, t11, t01)}" fill="{top}" stroke="{edge}" stroke-width="{sw}" stroke-linejoin="round"/>')


def roulette(x: float, y: float, value: str, size: float, start: float, dur: float = 27) -> tuple[str, str]:
    """Sayaç ruleti: her basamak kendi maskesinde dikey şerit, power2.out."""
    svg, css = [], []
    cx = x
    lh = size * 1.0
    for i, ch in enumerate(value):
        cw = K.text_width(ch, size, 800, -0.03)
        if not ch.isdigit():
            svg.append(f'<text class="bi" x="{cx:.1f}" y="{y:.1f}" font-family="{K.FONT}" font-size="{size}" '
                       f'font-weight="800" fill="{K.INK}"{K.delay(start + dur - 6)}>{ch}</text>')
            cx += cw
            continue
        seq = list(range(10)) * (1 + i // 2) + list(range(int(ch) + 1))
        n = len(seq) - 1
        col = "".join(f'<text x="{cx:.1f}" y="{y + k * lh:.1f}">{v}</text>' for k, v in enumerate(seq))
        svg.append(f'<clipPath id="r{i}"><rect x="{cx - 4:.1f}" y="{y - size * 0.82:.1f}" width="{cw + 8:.1f}" '
                   f'height="{size * 0.86:.1f}"/></clipPath><g clip-path="url(#r{i})">'
                   f'<g class="rl{i}" font-family="{K.FONT}" font-size="{size}" font-weight="800" fill="{K.INK}">{col}</g></g>')
        css.append(f".rl{i}{{animation:rl{i} {K.f(dur)} cubic-bezier(.33,1,.68,1) {K.f(start + i)} both}}"
                   f"@keyframes rl{i}{{from{{transform:translateY(0)}}to{{transform:translateY({-n * lh:.1f}px)}}}}")
        cx += cw
    return "".join(svg), "".join(css)


def main(src: str, dst: str) -> None:
    data = json.load(open(src, encoding="utf-8"))
    days = data["days"]

    # Pazar başlangıçlı haftalar (GitHub ile aynı)
    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7
    cells = []
    for i, d in enumerate(days):
        k = i + offset
        cells.append((k // 7, k % 7, d))
    weeks = cells[-1][0] + 1
    max_count = max(d["count"] for _, _, d in cells) or 1
    peak = max(cells, key=lambda c: (c[2]["count"], c[2]["date"]))   # eşitlikte en yeni gün

    def height(n: int) -> float:
        return H_MIN + (H_MAX - H_MIN) * math.sqrt(n / max_count)

    css = []
    parts = [f"<defs>{K.hatch_pattern('hw', K.HATCH)}{K.hatch_pattern('ho', K.ORANGE_HATCH)}"
             f"{K.hatch_pattern('hd', '#2E2E2E')}</defs>"]
    pw, pd = peak[0], peak[1]

    def occludes(w: int, d: int) -> bool:
        # Odağın önünde kalan komşular (ön sıralar ve soldaki hafta)
        return (d > pd and pw - 4 <= w <= pw + 1) or (d == pd and pw - 2 <= w < pw)

    # Zemin nokta tozu: şehirle aynı düzlemde, ~18 px aralık
    dust = []
    for w in range(-14, weeks + 10, 2):
        for d in range(-16, 22, 2):
            x, y = P(w + 0.5, d + 0.5)
            if 8 < x < K.W - 8 and 250 < y < H - 34:
                dust.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="0.9"/>')
    parts.append(f'<g fill="{K.DUST}" class="fade"{K.delay(0)}>{"".join(dust)}</g>')

    # Ay etiketleri: şehrin arka kenarı boyunca, gri
    labels, last = [], None
    for w, d, day in cells:
        m = date.fromisoformat(day["date"]).month
        if d == 6 and m != last and 0 < w < weeks - 1:
            x, y = P(w + 0.1, 8.3)
            labels.append(f'<text x="{x:.1f}" y="{y:.1f}">{MONTHS[m - 1]}</text>')
            last = m
    parts.append(f'<g font-family="{K.FONT}" font-size="10.5" font-weight="500" fill="{K.GREY_PASSIVE}" '
                 f'class="fade"{K.delay(6)}>{"".join(labels)}</g>')

    # Ressam sırası: arkadan öne (d − w artan)
    rise_end = 0
    for w, d, day in sorted(cells, key=lambda c: (c[1] - c[0], c[1])):
        fr = 10 + w * 0.9 + d * 0.35
        n = day["count"]
        if n == 0:
            a, b, c, e = w + GAP, w + 1 - GAP, d + GAP, d + 1 - GAP
            parts.append(f'<polygon class="fade" points="{K.pts(P(a, c), P(b, c), P(b, e), P(a, e))}" fill="none" '
                         f'stroke="#2E2E2E" stroke-width="0.8"{K.delay(fr)}/>')
            continue
        h = height(n)
        body = prism(w, d, h, K.INK2, "#E8E8E8", "hw")
        if occludes(w, d):
            # Odak turuncuya dönerken komşu ~%30 parlaklığa söner; siyah dolgu opak kalır
            body += f'<g class="fade orange"{K.delay(95)}>{prism(w, d, h, "#4A4A4A", "#4A4A4A", "hd")}</g>'
        if (w, d) == (pw, pd):
            # Önce beyaz yükselir, son anda turuncuya döner (3–4 kare)
            body += f'<g class="fade orange"{K.delay(95)}>{prism(w, d, h, K.ORANGE_FACE, K.ORANGE_LINE, "ho")}</g>'
        parts.append(f'<g class="rise"{K.delay(fr)}><title>{day["date"]}: {n} katkı</title>{body}</g>')
        rise_end = max(rise_end, fr + 6)
    css.append(".orange{animation-duration:" + K.f(3) + "}")

    # En yoğun gün etiketi: turuncu prizmadan yukarı ince çizgi
    pday = peak[2]
    tx, ty = P(pw + 0.5, pd + 0.5, height(pday["count"]))
    ly = ty - 34
    css.append(".lead{stroke-dasharray:40;stroke-dashoffset:40;animation:lead " + K.f(8) +
               " cubic-bezier(.45,0,.55,1) " + K.f(99) + " forwards}@keyframes lead{to{stroke-dashoffset:0}}")
    parts.append(f'<line class="lead" x1="{tx:.1f}" y1="{ty - 3:.1f}" x2="{tx:.1f}" y2="{ly + 6:.1f}" stroke="{K.ORANGE_LINE}" stroke-width="1.2"/>')
    peak_date = date.fromisoformat(pday["date"])
    label = f'{peak_date.day} {MONTHS[peak_date.month - 1]} · {pday["count"]} katkı'
    anchor_x = min(tx, K.W - 24 - K.text_width("en yoğun gün " + label, 16, 500))
    lbl, _, _ = K.masked_words(anchor_x, ly, [("en yoğun gün", 700, K.ORANGE), (label, 400, K.GREY_BACK)],
                               16, 104, step=2, uid="pk")
    parts.append(lbl)

    # Yazı bloğu, sol üst: bağlam ince, cevap kalın
    t1, _, _ = K.masked_words(K.LEFT, 70, [("Son 12 ayda", 300, K.INK)], 30, 0, uid="a")
    num = f'{data["total"]:,}'.replace(",", ".")
    rsvg, rcss = roulette(K.LEFT - 4, 168, num, 104, 4)
    css.append(rcss)
    t2, _, _ = K.masked_words(K.LEFT, 212, [("katkı.", 800, K.INK)], 30, 32, uid="b")
    stats = (f'güncel seri {data["current_streak"]} gün', f'en uzun seri {data["longest_streak"]} gün')
    t3, _, _ = K.masked_words(K.LEFT, 246, [(stats[0] + " ·", 400, K.GREY_2), (stats[1], 400, K.GREY_2)],
                              16, 40, step=1, uid="c")
    parts += [t1, rsvg, t2, t3]

    # Kaynak satırı, sol alt
    parts.append(f'<text class="fade" x="{K.LEFT}" y="{H - 18}" font-family="{K.FONT}" font-size="12.5" '
                 f'fill="{K.GREY_SRC}"{K.delay(20)}>Kaynak: github.com/{data["user"]} · her gün güncellenir · '
                 f'son güncelleme {days[-1]["date"]}</text>')

    svg = K.svg_open(H, "".join(css)) + "\n".join(parts) + "\n</svg>\n"
    with open(dst, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"yazıldı: {dst} ({weeks} hafta, {len(svg) // 1024} KB)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
