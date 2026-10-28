"""Giriş görseli: solda isim (ince bağlam + kalın cevap), sağda beyaz ASCII portre.

Portre satır satır, iki tempoyla yazılır (önce yavaş, sonra ivmelenir). Turuncu nokta portrede imleç
olarak doğar, yay çizerek ismin sonuna uçar ve cümle noktası olur: karedeki tek turuncu.
Kullanım: python scripts/make_hero_svg.py assets/portrait_prepped.png hero.svg
"""
import sys
from xml.sax.saxutils import escape

import kerem as K
from make_ascii_svg import to_ascii

H = 380
COLS = 76
CHAR_W = 4.6
LINE_H = CHAR_W / 0.6
PORTRAIT_X = 452
RAMP = ".:-=+*#%@"           # siyah zemin: parlak piksel yoğun karakter

NAME = ("Mustafa", "Tungur")
HELLO = "Merhaba, ben"
ROLE = "E-ticaret · dijital pazarlama · otomasyon"
ORG = "Mukas Pazarlama · Mama Keyfi"
SOURCE = "github.com/mustafatungur1"


def main(src: str, dst: str) -> None:
    lines = to_ascii(src, COLS, CHAR_W, LINE_H, RAMP)
    top = H - len(lines) * LINE_H          # büst alt kenara yaslı, çerçeve keser
    parts, css = [], []

    # Zemin nokta tozu: sol yarıda perspektifli zemin, ufka doğru sıklaşır
    dust, y, scale = [], H - 10.0, 1.0
    for _ in range(7):                     # 7 sıra, her biri öncekinin %82'si
        x = K.LEFT - 40
        while x < PORTRAIT_X - 20:
            dust.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{0.9 * scale + 0.2:.2f}"/>')
            x += 18 * scale
        y -= 20 * scale
        scale *= 0.82
    parts.append(f'<g fill="{K.DUST}" class="fade"{K.delay(0)}>{"".join(dust)}</g>')

    # Portre: her satır soldan sağa maskeyle açılır; aralık 4 kareden 1 kareye ivmelenir
    clips, texts, fr = [], [], 4.0
    width = COLS * CHAR_W
    for i, line in enumerate(lines):
        yy = top + i * LINE_H
        clips.append(f'<clipPath id="p{i}"><rect x="{PORTRAIT_X}" y="{yy:.1f}" width="0" height="{LINE_H + 1:.1f}">'
                     f'<animate attributeName="width" from="0" to="{width:.0f}" begin="{K.f(fr)}" dur="{K.f(4)}" '
                     f'fill="freeze"/></rect></clipPath>')
        texts.append(f'<text x="{PORTRAIT_X}" y="{yy + LINE_H * 0.8:.1f}" clip-path="url(#p{i})">'
                     f'{escape(line).replace(" ", chr(0xA0))}</text>')
        fr += max(1.0, 4.0 - i * 0.12)
    portrait_end = fr + 4
    parts.append(f'<defs>{"".join(clips)}</defs>')
    parts.append(f'<g fill="{K.INK2}" font-family="{K.MONO}" font-size="{CHAR_W / 0.6:.2f}" '
                 f'style="white-space:pre">{"".join(texts)}</g>')

    # Yazı bloğu: bağlam ince, isim kalın; kelime başına bir olay
    t1, _, _ = K.masked_words(K.LEFT, 104, [(HELLO, 300, K.INK)], 28, 0, uid="h")
    t2, _, _ = K.masked_words(K.LEFT, 176, [(NAME[0], 800, K.INK)], 66, 6, uid="n1")
    t3, end_x, _ = K.masked_words(K.LEFT, 244, [(NAME[1], 800, K.INK)], 66, 10, uid="n2")
    t4, _, _ = K.masked_words(K.LEFT, 290, [(ROLE, 300, K.GREY_BACK)], 18, 18, step=1.5, uid="r")
    t5, _, _ = K.masked_words(K.LEFT, 318, [(ORG, 500, K.GREY_2)], 15, 26, step=1.5, uid="o")
    parts += [t1, t2, t3, t4, t5]

    # Turuncu nokta: portrede imleç → yay uçuşu (6 kare) → iniş ezilmesi (1 kare) → cümle noktası
    r = 7.5
    dot_x, dot_y = end_x + 6 + r, 244 - r
    start_x, start_y = PORTRAIT_X + width * 0.5, top + 26
    dx, dy = start_x - dot_x, start_y - dot_y
    t_born, t_fly = portrait_end, portrait_end + 10
    css.append(
        f".dot{{opacity:0;animation:born {K.f(1)} linear {K.f(t_born)} forwards,"
        f"fly {K.f(6)} cubic-bezier(.33,1,.68,1) {K.f(t_fly)} both}}"
        "@keyframes born{to{opacity:1}}"
        f"@keyframes fly{{0%{{transform:translate({dx:.1f}px,{dy:.1f}px)}}"
        f"50%{{transform:translate({dx * 0.45:.1f}px,{dy * 0.45 - 70:.1f}px)}}"
        "100%{transform:translate(0,0)}}"
        f".land{{transform-box:fill-box;transform-origin:50% 100%;"
        f"animation:land {K.f(3)} linear {K.f(t_fly + 6)} both}}"
        "@keyframes land{0%{transform:scale(1.3,.8)}100%{transform:none}}"
        f".blink{{animation:blink {K.f(16)} steps(1) {K.f(t_born)} 1 both}}"
        "@keyframes blink{0%,50%{opacity:1}25%,75%{opacity:0}100%{opacity:1}}"
    )
    parts.append(f'<g class="dot"><g class="blink"><circle class="land" cx="{dot_x:.1f}" cy="{dot_y:.1f}" r="{r}" '
                 f'fill="{K.ORANGE}"/></g></g>')

    # Kaynak satırı, sol alt
    parts.append(f'<text class="fade" x="{K.LEFT}" y="{H - 18}" font-family="{K.FONT}" font-size="12.5" '
                 f'fill="{K.GREY_SRC}"{K.delay(30)}>{SOURCE}</text>')

    svg = K.svg_open(H, "".join(css)) + "\n".join(parts) + "\n</svg>\n"
    with open(dst, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"yazıldı: {dst} ({len(lines)} satır, {len(svg) // 1024} KB)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
