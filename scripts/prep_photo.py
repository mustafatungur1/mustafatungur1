"""Fotoğrafı ASCII'ye hazırlar: arka planı sil, kırp, kontrastı aç, gri ton + alfa maskesi.

Kullanım: python scripts/prep_photo.py assets/photo.jpeg assets/portrait_prepped.png
Yalnızca yerelde çalıştırılır (rembg ağır bir bağımlılık).
"""
import sys

import cv2
import numpy as np
from PIL import Image, ImageOps
from rembg import remove

# Baş + omuz kadrajı (kaynak görsel oranına göre: sol, üst, sağ, alt)
CROP = (0.15, 0.23, 0.75, 0.62)


def main(src: str, dst: str) -> None:
    img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")  # iPhone döndürmesi
    w, h = img.size
    l, t, r, b = CROP
    img = img.crop((int(w * l), int(h * t), int(w * r), int(h * b)))

    cut = remove(img)  # RGBA, arka plan şeffaf
    alpha = np.array(cut.split()[-1]).astype(np.float32) / 255.0

    gray = cv2.cvtColor(np.array(cut.convert("RGB")), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    gray = clahe.apply(gray).astype(np.float32)

    # Gri + alfa olarak kaydet: alfa ASCII'de arka planı boşluk yapar
    out = np.dstack([gray.clip(0, 255), alpha * 255.0]).astype(np.uint8)
    Image.fromarray(out, "LA").save(dst)
    print(f"yazıldı: {dst} {out.shape[1]}x{out.shape[0]}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
