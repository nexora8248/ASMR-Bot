import os
import requests
import json
import shutil
from datetime import datetime

# GitHub Secrets
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

VIDEOS_DIR = 'videos'
HISTORY_FILE = 'history.json'

# 1. History load karna aur format check karna
history = {}
if os.path.exists(HISTORY_FILE):
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                history = data
            else:
                history = {} # Agar list hai to reset kar do
    except json.JSONDecodeError:
        history = {}

now = datetime.now()
current_history = history.copy()

# 2. 15 din purane video delete karna
print("Checking for videos older than 15 days...")
for vid_name, date_str in history.items():
    try:
        vid_date = datetime.fromisoformat(date_str)
        if (now - vid_date).days >= 15:
            vid_path = os.path.join(VIDEOS_DIR, vid_name)
            if os.path.exists(vid_path):
                os.remove(vid_path)
                print(f"Deleted: {vid_name}")
            if vid_name in current_history:
                del current_history[vid_name]
    except Exception as e:
        print(f"Error checking date for {vid_name}: {e}")

# 3. Naya video select karna
if not os.path.exists(VIDEOS_DIR):
    os.makedirs(VIDEOS_DIR)

all_videos = [f for f in os.listdir(VIDEOS_DIR) if f.endswith('.mp4')]
new_video = next((v for v in all_videos if v not in current_history), None)

if not new_video:
    print("No new video to post.")
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(current_history, f, indent=4)
    exit(0)

video_path = os.path.join(VIDEOS_DIR, new_video)

# 4. Telegram & Webhook details
title = f"Video: {new_video}"
caption = f"*{title}*\n\n#automation #telegram"

print(f"Posting: {new_video}")
try:
    # Telegram
    tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    with open(video_path, 'rb') as f:
        tg_res = requests.post(tg_url, data={'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'Markdown'}, files={'video': f}).json()

    video_link = "N/A"
    if tg_res.get('ok'):
        msg_id = tg_res['result']['message_id']
        clean_chat_id = str(CHAT_ID).replace('@', '')
        video_link = f"https://t.me/{clean_chat_id}/{msg_id}"

    # Webhook
    requests.post(WEBHOOK_URL, json={"video_link": video_link, "title": title, "caption": caption})

    # History update
    current_history[new_video] = now.isoformat()
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(current_history, f, indent=4)
    print("Success!")

except Exception as e:
    print(f"Error during upload: {e}")
