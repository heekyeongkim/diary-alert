# -*- coding: utf-8 -*-
import json
import os
import random
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))
DIARY_URL = "https://claude.ai/cowork/project/019f6168-8bab-7505-9aac-e7d131654a73"


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
            f"📝 어젯밤 수면시간을 기록해주세요\n"
            f"아래 버튼을 눌러 \"수면 ○시간\"이라고 남기면 됩니다"
        )
    else:
        return (
            f"🌙 <b>하루 마무리 시간입니다</b>  {date_str}\n\n"
            f"{quote}\n\n"
            f"📔 오늘 하루를 정리해볼까요?\n"
            f"아래 버튼을 눌러 \"일기 시작\"이라고 입력하세요"
        )


def send_telegram(text: str):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [[
                {"text": "📔 일기 쓰러 가기", "url": DIARY_URL}
            ]]
        },
    }).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    if not result.get("ok"):
        raise RuntimeError(f"Telegram API error: {result}")
    print("[OK] alert sent")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "morning"
    if mode not in ("morning", "evening"):
        print("사용법: python send_diary_alert.py morning|evening")
        sys.exit(1)
    send_telegram(build_message(mode))
