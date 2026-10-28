"""Ortak görsel dil: siyah zemin, beyaz grotesk, tek turuncu vurgu, ışıksız izometrik yüzler.

Ölçüler 1920 genişlikli referanstan 860'a ölçeklenir (S = 0.448). Süreler 30 fps karesi cinsinden.
"""
import base64
import os
from xml.sax.saxutils import escape

S = 860 / 1920
W = 860
LEFT = round(118 * S)          # sol kenar

BG = "#000000"
INK = "#FFFFFF"
INK2 = "#F0F0F0"
GREY_BACK = "#BDBDBD"          # geri çekilen satır
GREY_2 = "#A0A0A0"             # ikincil satır, etiket
GREY_SRC = "#A5A5A5"           # kaynak satırı
GREY_PASSIVE = "#6A6A6A"
DUST = "#2A2A2A"               # zemin nokta tozu
ORANGE = "#FF5A0A"
ORANGE_FACE = "#FF5410"
ORANGE_LINE = "#E8501A"
ORANGE_HATCH = "#8A3418"
HATCH = "#7A7A7A"

FPS = 30
FONT = "'Inter Tight',Inter,'Helvetica Neue',Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

_FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")


def f(frames: float) -> str:
    """Kare → CSS saniye."""
    return f"{frames / FPS:.3f}s"


def font_face() -> str:
    """Inter Tight (değişken, 100–900) SVG içine gömülü; <img> içinde dış font yüklenmez."""
    out = []
    for name, rng in (("latin", "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215"),
                      ("latin-ext", "U+0100-02AF,U+0304,U+0308,U+0329,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF")):
        data = base64.b64encode(open(os.path.join(_FONT_DIR, f"InterTight-{name}.woff2"), "rb").read()).decode()
        out.append("@font-face{font-family:'Inter Tight';font-weight:100 900;font-display:block;"
                   f"src:url(data:font/woff2;base64,{data}) format('woff2');unicode-range:{rng}}}")
    return "".join(out)


# Giriş kalıpları (rehber 9.5). Hepsi bir kez oynar ve son karede durur.
BASE_CSS = (
    # Kelime maskesi: alttan kayar + opaklık, 3–4 kare, power3.out, taşmasız
    ".wm{opacity:0;transform-box:fill-box;transform:translateY(100%);animation:wm " + f(4) + " cubic-bezier(.215,.61,.355,1) forwards}"
    "@keyframes wm{to{opacity:1;transform:none}}"
    # Blur-in, 5 kare
    ".bi{opacity:0;filter:blur(6px);animation:bi " + f(5) + " cubic-bezier(.25,.46,.45,.94) forwards}"
    "@keyframes bi{to{opacity:1;filter:blur(0)}}"
    # Daktilo rengi: gri doğar, 3 karede beyaz
    ".ty{opacity:0;fill:#808080;animation:ty " + f(3) + " ease-out forwards}"
    "@keyframes ty{0%{opacity:1;fill:#808080}100%{opacity:1;fill:" + INK + "}}"
    # Zeminden yükselme: scaleY 0→1, pivot taban, taşmasız power3.out
    ".rise{transform-box:fill-box;transform-origin:50% 100%;transform:scaleY(0);"
    "animation:rise " + f(6) + " cubic-bezier(.215,.61,.355,1) forwards}"
    "@keyframes rise{to{transform:scaleY(1)}}"
    # Küçük pop: back.out(1.5)
    ".pop{transform-box:fill-box;transform-origin:50% 50%;transform:scale(0);"
    "animation:pop " + f(5) + " cubic-bezier(.34,1.56,.64,1) forwards}"
    "@keyframes pop{to{transform:scale(1)}}"
    ".fade{opacity:0;animation:fade " + f(6) + " linear forwards}"
    "@keyframes fade{to{opacity:1}}"
)


def svg_open(height: int, css: str = "", fonts: bool = True) -> str:
    style = (font_face() if fonts else "") + BASE_CSS + css
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}">\n'
            f"<style>{style}</style>\n"
            f'<rect width="{W}" height="{height}" rx="14" fill="{BG}"/>\n')


def delay(frames: float) -> str:
    return f' style="animation-delay:{f(frames)}"'


def masked_words(x: float, y: float, parts: list[tuple[str, int, str]], size: float,
                 start: float, step: float = 3, gap: float = 0.26, track: float = -0.02,
                 uid: str = "w") -> tuple[str, float, float]:
    """Kelime maskesiyle giren satır. parts: (metin, ağırlık, renk). Kelime başına bir olay.

    Dönüş: (svg, satır sonu x, son kelimenin başlama karesi). Genişlik tahmini Inter Tight
    ortalama harf genişliğine göre yapılır (gerçek ölçüm SVG içinde mümkün değil).
    """
    out, cx, fr = [], x, start
    words = [(w, wt, col) for text, wt, col in parts for w in text.split(" ") if w]
    for i, (w, wt, col) in enumerate(words):
        clip = f"{uid}{i}"
        wdt = text_width(w, size, wt, track)
        out.append(f'<clipPath id="{clip}"><rect x="{cx - 2:.1f}" y="{y - size * 1.0:.1f}" '
                   f'width="{wdt + size * 0.2:.1f}" height="{size * 1.28:.1f}"/></clipPath>'
                   f'<g clip-path="url(#{clip})"><text class="wm" x="{cx:.1f}" y="{y:.1f}" font-family="{FONT}" '
                   f'font-size="{size:.1f}" font-weight="{wt}" letter-spacing="{track}em" fill="{col}"'
                   f'{delay(fr)}>{escape(w)}</text></g>')
        cx += wdt + size * gap
        fr += step
    return "".join(out), cx - size * gap, fr - step


_FONTS: dict = {}


def _font(name: str, weight: int):
    key = (name, weight)
    if key not in _FONTS:
        from PIL import ImageFont
        fnt = ImageFont.truetype(os.path.join(_FONT_DIR, f"InterTight-{name}.woff2"), 200)
        fnt.set_variation_by_axes([weight])
        _FONTS[key] = fnt
    return _FONTS[key]


def text_width(s: str, size: float, weight: int = 400, track: float = 0) -> float:
    """Gömülü Inter Tight ile gerçek genişlik; Türkçe harfler latin-ext dosyasından ölçülür."""
    total, run, ext = 0.0, "", None
    for ch in s + "\0":
        is_ext = ch != "\0" and 0x100 <= ord(ch) <= 0x2AF and ch != "ı"
        if ch == "\0" or (ext is not None and is_ext != ext):
            if run:
                total += _font("latin-ext" if ext else "latin", weight).getlength(run)
            run = ""
        if ch != "\0":
            run += ch
            ext = is_ext
    return total / 200 * size + track * size * len(s)


def hatch_pattern(pid: str, color: str, spacing: float = 3.0, angle: float = 45) -> str:
    """Ekran uzayında diyagonal tarama: siyah üstüne ~1 px çizgi (yüzle dönmez)."""
    return (f'<pattern id="{pid}" patternUnits="userSpaceOnUse" width="{spacing}" height="{spacing}" '
            f'patternTransform="rotate({angle})"><rect width="{spacing}" height="{spacing}" fill="#000"/>'
            f'<line x1="0" y1="0" x2="0" y2="{spacing}" stroke="{color}" stroke-width="0.8"/></pattern>')


def pts(*ps) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in ps)
