"""GitHub'ın herkese açık katkı takviminden günlük veriyi çeker (token gerekmez).

Kullanım: python scripts/fetch_contributions.py <kullanıcı> data/contributions.json
"""
import json
import re
import sys
from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup


def fetch(user: str) -> list[dict]:
    r = requests.get(
        f"https://github.com/users/{user}/contributions",
        headers={"User-Agent": "profile-art-bot", "X-Requested-With": "XMLHttpRequest"},
        timeout=30,
    )
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Sayılar, hücreye for= ile bağlı tool-tip içinde: "5 contributions on May 3rd."
    counts = {}
    for tip in soup.select("tool-tip[for]"):
        m = re.match(r"\s*(\d+|No) contribution", tip.get_text())
        if m:
            counts[tip["for"]] = 0 if m.group(1) == "No" else int(m.group(1))

    days = []
    for td in soup.select("td.ContributionCalendar-day[data-date]"):
        days.append({
            "date": td["data-date"],
            "level": int(td.get("data-level", 0)),
            "count": counts.get(td.get("id"), 0),
        })
    days.sort(key=lambda d: d["date"])
    return days


def streaks(days: list[dict]) -> tuple[int, int]:
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)
    # Güncel seri: bugün henüz katkı yoksa dünden geriye say
    current = 0
    active = {d["date"] for d in days if d["count"] > 0}
    day = date.fromisoformat(days[-1]["date"])
    if day.isoformat() not in active:
        day -= timedelta(days=1)
    while day.isoformat() in active:
        current += 1
        day -= timedelta(days=1)
    return current, longest


def main(user: str, dst: str) -> None:
    days = fetch(user)
    if not days:
        sys.exit("katkı verisi bulunamadı — GitHub HTML yapısı değişmiş olabilir")
    current, longest = streaks(days)
    data = {
        "user": user,
        "total": sum(d["count"] for d in days),
        "current_streak": current,
        "longest_streak": longest,
        "days": days,
    }
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"yazıldı: {dst} — {len(days)} gün, toplam {data['total']}, seri {current}/{longest}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
