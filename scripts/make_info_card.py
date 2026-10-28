"""Profil bilgi kartı SVG'si. Bilgileri aşağıdaki NAME / TITLE / INFO alanlarından düzenle.

STATIC=1 ile animasyonsuz kare üretir.
Kullanım: python scripts/make_info_card.py info-card.svg
"""
import os
import sys
from xml.sax.saxutils import escape

NAME = "Mustafa Tungur"
TITLE = "E-ticaret & Dijital Pazarlama"
INFO = [
    ("Şirket", "Mukas Pazarlama"),
    ("Proje", "Mama Keyfi · pet e-ticaret"),
    ("Backend", "Laravel 13 · Filament 5 · PHP"),
    ("Reklam", "Meta Ads · Google Ads"),
    ("İçerik", "Video üretimi · Remotion"),
    ("Yapay zekâ", "Claude Code · üretken medya"),
    ("Odak", "Otomasyon · veri · büyüme"),
]
FOOTER = "github.com/mustafatungur1"

WIDTH = 410
HEIGHT = 410
PAD = 28
BAR_H = 30
LINE_H = 30
FONT = 13
KEY_W = 96            # anahtar sütunu genişliği
BG = "#ffffff"
BAR = "#f6f8fa"
BORDER = "#d0d7de"
TEXT = "#1f2328"
DIM = "#656d76"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"


def main(dst: str) -> None:
    static = os.environ.get("STATIC") == "1"
    css = "" if static else (
        "<style>"
        ".l{opacity:0;animation:in .4s ease-out forwards}"
        "@keyframes in{from{opacity:0;transform:translateY(3px)}to{opacity:1;transform:none}}"
        ".cur{animation:blink 1.1s steps(1) infinite}"
        "@keyframes blink{50%{opacity:0}}"
        "</style>"
    )

    def g(i: int, body: str) -> str:
        delay = f' style="animation-delay:{0.3 + i * 0.12:.2f}s"' if not static else ""
        return f'<g class="l"{delay}>{body}</g>'

    y = BAR_H + PAD + 22
    out = [g(0, f'<text x="{PAD}" y="{y}" font-family="{SANS}" font-size="22" font-weight="700" '
                f'fill="{TEXT}">{escape(NAME)}</text>')]
    y += 24
    out.append(g(1, f'<text x="{PAD}" y="{y}" font-family="{SANS}" font-size="14" fill="{DIM}">'
                    f'{escape(TITLE)}</text>'))
    y += 20
    out.append(g(2, f'<line x1="{PAD}" y1="{y}" x2="{WIDTH - PAD}" y2="{y}" stroke="{BORDER}"/>'))
    y += 12
    for j, (k, v) in enumerate(INFO):
        y += LINE_H
        out.append(g(3 + j, f'<text y="{y}" font-family="{MONO}" font-size="{FONT}">'
                            f'<tspan x="{PAD}" fill="{DIM}">{escape(k)}</tspan>'
                            f'<tspan x="{PAD + KEY_W}" fill="{TEXT}">{escape(v)}</tspan></text>'))

    fy = HEIGHT - PAD + 4
    cursor = (f'<rect class="cur" x="{PAD + (len(FOOTER) + 2) * FONT * 0.6 + 4:.0f}" y="{fy - 12}" '
              f'width="7" height="15" fill="{TEXT}"/>' if not static else "")
    out.append(g(4 + len(INFO), f'<text x="{PAD}" y="{fy}" font-family="{MONO}" font-size="{FONT}" fill="{DIM}">'
                                f'<tspan fill="{TEXT}">→</tspan> {escape(FOOTER)}</text>{cursor}'))

    dots = "".join(f'<circle cx="{18 + n * 18}" cy="{BAR_H / 2}" r="5.5" fill="{c}"/>'
                   for n, c in enumerate(["#d0d7de"] * 3))
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">\n'
        f"{css}\n"
        f'<rect x=".5" y=".5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>\n'
        f'<path d="M.5 {BAR_H}V10.5a10 10 0 0 1 10-10h{WIDTH - 21}a10 10 0 0 1 10 10V{BAR_H}z" fill="{BAR}"/>\n'
        f'<line x1=".5" y1="{BAR_H}" x2="{WIDTH - .5}" y2="{BAR_H}" stroke="{BORDER}"/>\n'
        f'{dots}<text x="{WIDTH / 2}" y="{BAR_H / 2 + 4}" text-anchor="middle" fill="{DIM}" '
        f'font-family="{MONO}" font-size="11.5">about.md</text>\n'
        + "\n".join(out) + "\n</svg>\n"
    )
    with open(dst, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"yazıldı: {dst}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "info-card.svg")
