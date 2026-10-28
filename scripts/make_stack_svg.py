"""Yığın görseli: "Neyle kuruyorum?" — katmanlar aşağıdan yukarı izometrik levhalar olarak kurulur.

Her satır yazıldığı anda kendi levhası yukarıdan iner (nesne yazıdan 1 kare önce). En üst levha ürün:
yazıda turuncu doğar, levha turuncu oturunca yazı beyaza döner (kavram nesneye geçer).
Kullanım: python scripts/make_stack_svg.py stack.svg
"""
import math
import sys

import kerem as K

H = 420
# Alttan üste: (anahtar, değer). Son katman ürün, turuncu.
LAYERS = [
    ("Altyapı", "Laravel 13 · Filament 5 · PHP"),
    ("Reklam", "Meta Ads · Google Ads"),
    ("İçerik", "Video üretimi · Remotion · HyperFrames"),
    ("Yapay zekâ", "Claude Code · üretken medya"),
    ("Ürün", "Mama Keyfi"),
]

SIZE = 104                     # levha kenarı (izometrik birim)
CX, BASE_Y = 652, H - 24 - SIZE / 2   # yığının zemin merkezi; alt köşe kenara 24 px
THICK, GAP = 20, 12
ROW_Y0, ROW_DY = 150, 50
X_AX = (math.cos(math.radians(30)), math.sin(math.radians(30)))
Y_AX = (-math.cos(math.radians(30)), math.sin(math.radians(30)))


def P(x: float, y: float, z: float = 0) -> tuple[float, float]:
    """Zemin (x, y) ve yükseklik z → ekran. Levha merkezi (0, 0)."""
    return CX + x * X_AX[0] + y * Y_AX[0], BASE_Y + x * X_AX[1] + y * Y_AX[1] - z


def slab(z: float, top: str, edge: str, hatch: str) -> str:
    s = SIZE / 2
    b = [P(-s, -s, z), P(s, -s, z), P(s, s, z), P(-s, s, z)]
    t = [P(-s, -s, z + THICK), P(s, -s, z + THICK), P(s, s, z + THICK), P(-s, s, z + THICK)]
    kw = f'stroke="{edge}" stroke-width="1.2" stroke-linejoin="round"'
    return (f'<polygon points="{K.pts(b[3], b[2], t[2], t[3])}" fill="#000" {kw}/>'        # sol yan: siyah
            f'<polygon points="{K.pts(b[1], b[2], t[2], t[1])}" fill="url(#{hatch})" {kw}/>'  # sağ yan: taralı
            f'<polygon points="{K.pts(*t)}" fill="{top}" {kw}/>')


def main(dst: str) -> None:
    parts = [f"<defs>{K.hatch_pattern('hw', K.HATCH, 3.2, 60)}{K.hatch_pattern('ho', K.ORANGE_HATCH, 3.2, 60)}</defs>"]
    css = []

    # Zemin nokta tozu: levhalarla aynı izometrik düzlemde
    dust = []
    for i in range(-12, 13):
        for j in range(-12, 13):
            x, y = P(i * 20, j * 20)
            if K.W * 0.42 < x < K.W - 10 and 250 < y < H - 8:
                dust.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="0.9"/>')
    parts.append(f'<g fill="{K.DUST}" class="fade"{K.delay(0)}>{"".join(dust)}</g>')

    # Başlık: soru ince + cevap kalın
    title, _, _ = K.masked_words(K.LEFT, 92, [("Neyle", 300, K.INK), ("kuruyorum?", 800, K.INK)], 46, 0, uid="t")
    parts.append(title)

    n = len(LAYERS)
    start = 12
    step = 10                                   # katmanlar arası kare
    for i, (key, val) in enumerate(LAYERS):
        fr = start + i * step
        z = i * (THICK + GAP)
        is_top = i == n - 1
        row_y = ROW_Y0 + (n - 1 - i) * ROW_DY   # üst katman en üst satırda

        # Levha: yukarıdan iner, taşmasız power3.out, 6 kare; yazıdan 1 kare önce
        body = slab(z, K.ORANGE_FACE if is_top else K.INK2, K.ORANGE_LINE if is_top else "#E8E8E8",
                    "ho" if is_top else "hw")
        parts.append(f'<g class="drop"{K.delay(fr - 1)}>{body}</g>')

        # Bağlantı çizgisi: satırdan levhanın sol köşesine, 1 px, düşük opaklık
        lx, ly = P(-SIZE / 2, SIZE / 2, z + THICK / 2)
        x0 = K.LEFT + max(K.text_width(val, 19, 500), K.text_width(key, 13, 400)) + 18
        parts.append(f'<line class="fade" x1="{x0:.1f}" y1="{row_y - 7:.1f}" x2="{lx - 6:.1f}" y2="{ly:.1f}" '
                     f'stroke="#FFFFFF" stroke-opacity=".28" stroke-width="1"{K.delay(fr + 4)}/>')

        k, _, _ = K.masked_words(K.LEFT, row_y - 21, [(key, 400, K.GREY_PASSIVE)], 13, fr, uid=f"k{i}")
        v, _, _ = K.masked_words(K.LEFT, row_y, [(val, 800 if is_top else 500, K.INK)], 19, fr + 1, step=1.5,
                                 uid=f"v{i}")
        if is_top:
            # Turuncu kopya üstte doğar; kavram levhaya geçince (12 kare sonra) söner, beyaz kalır
            vo, _, _ = K.masked_words(K.LEFT, row_y, [(val, 800, K.ORANGE)], 19, fr + 1, step=1.5, uid=f"vo{i}")
            v += f'<g class="toink">{vo}</g>'
            css.append(f".toink{{animation:out {K.f(6)} linear {K.f(fr + 18)} forwards}}"
                       "@keyframes out{to{opacity:0}}")
        parts += [k, v]

    css.append(".drop{opacity:0;transform:translateY(-36px);animation:drop " + K.f(6) +
               " cubic-bezier(.215,.61,.355,1) forwards}@keyframes drop{to{opacity:1;transform:none}}")

    svg = K.svg_open(H, "".join(css)) + "\n".join(parts) + "\n</svg>\n"
    with open(dst, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"yazıldı: {dst} ({len(svg) // 1024} KB)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "stack.svg")
