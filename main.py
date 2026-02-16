import os
import requests
import json
import shutil
from datetime import datetime, timedelta

# GitHub Secrets se data lena
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

VIDEOS_DIR = 'videos'
HISTORY_FILE = 'history.json'

# 1. History load karna aur 15 din purane video delete karna
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        history = json.load(f)
else:
    history = {}

now = datetime.now()
current_history = history.copy()

print("Checking for videos older than 15 days...")
for vid_name, date_str in history.items():
    vid_date = datetime.fromisoformat(date_str)
    if (now - vid_date).days >= 15:
        # Video file delete karna
        vid_path = os.path.join(VIDEOS_DIR, vid_name)
        if os.path.exists(vid_path):
            os.remove(vid_path)
            print(f"Deleted old video file: {vid_name}")
        # History se hatana
        if vid_name in current_history:
            del current_history[vid_name]

# 2. Naya video select karna jo history mein na ho
all_videos = [f for f in os.listdir(VIDEOS_DIR) if f.endswith('.mp4')]
new_video = None
for v in all_videos:
    if v not in current_history:
        new_video = v
        break

if not new_video:
    print("No new video to post.")
    # Purani history update karke save karna (purane delete hone ke baad)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(current_history, f, indent=4)
    exit(0)

video_path = os.path.join(VIDEOS_DIR, new_video)

# Caption aur Title (Aap isse manually yahan change kar sakte hain ya generic rakh sakte hain)
title = f"Video: {new_video}"
caption = f"{title}\n\n#automation #telegram #video"

# 3. Telegram par bhejna
print(f"Posting to Telegram: {new_video}")
tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
with open(video_path, 'rb') as f:
    tg_res = requests.post(
        tg_url,
        data={'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'Markdown'},
        files={'video': f}
    ).json()

# Telegram link nikalna
video_link = "N/A"
if tg_res.get('ok'):
    msg_id = tg_res['result']['message_id']
    clean_chat_id = str(CHAT_ID).replace('@', '')
    video_link = f"https://t.me/{clean_chat_id}/{msg_id}"

# 4. Webhook par data bhejna
webhook_payload = {
    "video_link": video_link,
    "title": title,
    "caption": caption,
    "status": "posted"
}
requests.post(WEBHOOK_URL, json=webhook_payload)

# 5. History update karna (Naya video aur current date add karna)
current_history[new_video] = now.isoformat()
with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
    json.dump(current_history, f, indent=4)

print("Process finished successfully.")
