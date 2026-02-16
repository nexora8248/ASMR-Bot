import os
import requests
import json
import random
from datetime import datetime

# GitHub Secrets
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
GITHUB_REPO = os.environ.get('GITHUB_REPOSITORY') # Auto-provided by GitHub Actions

VIDEOS_DIR = 'videos'
HISTORY_FILE = 'history.json'

# --- Universal Data Pool ---
TITLES = [
    "Amazing Moments", "Don't Miss This", "Life is Beautiful", "Daily Dose of Magic", 
    "Nature's Wonder", "Incredible Skill", "Pure Happiness", "Something Special",
    "Watch Until The End", "Mind Blowing", "A Day to Remember", "Heart Touching",
    "Simply The Best", "Experience Joy", "Unforgettable Vibes", "Classic Content",
    "Keep Smiling", "Positive Vibes Only", "Today's Highlight", "Golden Moments",
    "Stay Inspired", "Beyond Perfection", "Visual Treat", "Masterpiece", "Creative Mind",
    "Weekend Vibes", "Relaxing Time", "Adventure Awaits", "Dream Big", "Stay Focused",
    "Next Level", "Peaceful Escape", "Life's Short, Enjoy", "Awesome Energy",
    "The Secret of Joy", "Beautiful Journey", "Limitless Bliss", "Trending Now",
    "Must See", "Feel Good Post", "Epic Discovery", "Smooth & Clean", "Magic in Air",
    "Believe in Yourself", "True Beauty", "Wait for it", "Perfectly Done", "Inspiring",
    "Unseen Beauty", "Classic View", "World's Best", "Legendary Shot"
]

CAPTIONS = [
    "This will make your day!", "Success is a journey, not a destination.", "Every moment is a fresh beginning.",
    "Do more of what makes you happy.", "Life is better when you're laughing.", "Your vibe attracts your tribe.",
    "Collect moments, not things.", "Small steps every day lead to big results.", "Radiate positivity everywhere you go.",
    "The best is yet to come.", "Be a voice, not an echo.", "Turn your dreams into reality.",
    "Consistency is key.", "Stay humble, work hard, be kind.", "Happiness depends upon ourselves.",
    "Enjoy the little things in life.", "Focus on the good.", "Make today amazing.", "Dream it. Wish it. Do it.",
    "Kindness is free, sprinkle it everywhere.", "Don't stop until you're proud.", "Great things take time.",
    "Be the reason someone smiles today.", "Life is tough but so are you.", "Escape the ordinary.",
    "Follow your heart.", "Better things are coming.", "Believe you can and you're halfway there.",
    "Keep it simple.", "Stay true to yourself.", "Grateful for today.", "New day, new goals.",
    "Push yourself to the limit.", "Confidence is silent, insecurities are loud.", "Choose joy every single day.",
    "Live, laugh, love.", "Stop wishing, start doing.", "Create your own sunshine.", "The journey of a thousand miles begins with a single step.",
    "One day at a time.", "Seize the day.", "Be the change you want to see.", "Good things are coming.",
    "Everything happens for a reason.", "Keep glowing.", "Don't wait for opportunity, create it.",
    "Sunsets and silhouettes.", "Less perfection, more authenticity.", "Adventure is out there.",
    "Self-love is the best love.", "Quiet the mind and the soul will speak."
]

# SEO & Instagram Viral Hashtags
SEO_HASHTAGS = "#viral #trending #video #shorts #explore #reels #foryou #status #contentcreator #top #popular #dailyvideo #socialmedia #bestvideo #viralpost"
INSTA_SEO_HASHTAGS = "#instadaily #reelkarofeelkaro #trendingreels #viralvideos #explorepage"

# 1. History load & 15 days clean-up
history = {}
if os.path.exists(HISTORY_FILE):
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            history = data if isinstance(data, dict) else {}
    except: history = {}

now = datetime.now()
current_history = history.copy()

for vid, d_str in history.items():
    if (now - datetime.fromisoformat(d_str)).days >= 15:
        p = os.path.join(VIDEOS_DIR, vid)
        if os.path.exists(p): os.remove(p)
        if vid in current_history: del current_history[vid]

# 2. Pickup new video
all_vids = [f for f in os.listdir(VIDEOS_DIR) if f.endswith('.mp4')]
new_video = next((v for v in all_vids if v not in current_history), None)

if not new_video:
    with open(HISTORY_FILE, 'w') as f: json.dump(current_history, f, indent=4)
    exit(0)

# 3. Random Title & Caption selection
selected_title = random.choice(TITLES)
selected_caption = random.choice(CAPTIONS)

# 4. Generate GitHub Raw Link
# Format: https://raw.githubusercontent.com/username/repo/branch/videos/filename.mp4
raw_video_link = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{VIDEOS_DIR}/{new_video}"

# 5. Telegram Posting
full_msg = f"✨ *{selected_title}*\n\n{selected_caption}\n\n*SEO:* {SEO_HASHTAGS}\n\n*Insta:* {INSTA_SEO_HASHTAGS}"

try:
    tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    with open(os.path.join(VIDEOS_DIR, new_video), 'rb') as f:
        requests.post(tg_url, data={'chat_id': CHAT_ID, 'caption': full_msg, 'parse_mode': 'Markdown'}, files={'video': f})

    # 6. Webhook Posting
    webhook_data = {
        "video_link": raw_video_link,
        "title": selected_title,
        "caption": selected_caption,
        "seo_hashtags": SEO_HASHTAGS,
        "insta_hashtags": INSTA_SEO_HASHTAGS
    }
    requests.post(WEBHOOK_URL, json=webhook_data)

    # 7. Update History
    current_history[new_video] = now.isoformat()
    with open(HISTORY_FILE, 'w') as f: json.dump(current_history, f, indent=4)
    print(f"Posted: {new_video}")
except Exception as e:
    print(f"Error: {e}")
