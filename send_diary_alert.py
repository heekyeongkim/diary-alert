# -*- coding: utf-8 -*-
"""
일기 알림 봇 - 아침/저녁 명언과 함께 기록 리마인더 발송
사용법: python send_diary_alert.py morning|evening
환경변수: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
"""
import json
import os
import random
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))


def load_random_quote():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quotes.json")
    with open(path, encoding="utf-8") as f:
        quotes = json.load(f)
    q = random.choice(quotes)
    return f"\"{q['quote']}\"\n— {q['author']}"


def build_message(mode: str) -> str:
    now = datetime.now(KST)
    date_str = now.strftime("%Y-%m-%d (%a)")
    quote = load_random_quote()

    if mode == "morning":
        return (
            f"🌅 <b>좋은 아침입니다!</b>  {date_str}\n\n"
            f"{quote}\n\n"
            f"📝 오늘의 아침 기록\n"
            f"• 어젯밤 수면시간을 기록해주세요 (취침 → 기상)\n"
            f"• Claude 일기 프로젝트에 \"수면 ○시간\"이라고 남기면 됩니다"
        )
    else:  # evening
        return (
            f"🌙 <b>하루 마무리 시간입니다</b>  {date_str}\n\n"
            f"{quote}\n\n"
            f"📔 오늘의 일기\n"
            f"• Claude 일기 프로젝트를 열고 \"일기 시작\"이라고 입력하세요\n"
            f"• 하루를 정리하면 Notion에 저장됩니다"
        )


def send_telegram(text: str):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps(
        {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    ).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    if not result.get("ok"):
        raise RuntimeError(f"Telegram API error: {result}")
    print(f"[OK] {datetime.now(KST).isoformat()} - {sys.argv[1]} alert sent")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "morning"
    if mode not in ("morning", "evening"):
        print("사용법: python send_diary_alert.py morning|evening")
        sys.exit(1)
    send_telegram(build_message(mode))
