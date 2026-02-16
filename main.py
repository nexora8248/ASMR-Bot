import os
import requests
import json
import random
from datetime import datetime

# GitHub Secrets
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
GITHUB_REPO = os.environ.get('GITHUB_REPOSITORY')

VIDEOS_DIR = 'videos'
HISTORY_FILE = 'history.json'

# --- ASMR USA Targeted Data Pool (50+ Titles & Captions) ---
TITLES = [
    "Relaxing ASMR Tingles", "Deep Sleep Triggers", "Satisfying Slime Sounds", "Ultra Quiet Whispers",
    "Brain Melting ASMR", "The Ultimate Relaxation", "Crushing Soft Things", "ASMR for Anxiety Relief",
    "No Talking Just Tingles", "Oddly Satisfying ASMR", "Visual Triggers for Sleep", "Fast & Aggressive ASMR",
    "Soap Carving Therapy", "Kinetic Sand Cutting", "Tingly Ear Massage", "Intense Mouth Sounds",
    "Gentle Tapping & Scratching", "Water Droplet Sounds", "ASMR Cooking Sounds", "Microphone Brushing",
    "Page Turning Softly", "Keyboard Typing ASMR", "Ice Crushing Sounds", "Wood Fire Crackling",
    "Rainy Night Relaxation", "Stress Relief ASMR", "Sleep Induction Sounds", "Hand Movements ASMR",
    "Personal Attention ASMR", "Meditation & Tingles", "Nature ASMR Therapy", "Soft Foam Squishing",
    "Brush Sounds on Mic", "Deep Relaxation Journey", "ASMR for Deep Focus", "Hypnotic ASMR Visuals",
    "Lofi ASMR Vibes", "Tingly Scalp Massage", "Calming Fabric Sounds", "Satisfying Crunchy ASMR",
    "ASMR Magic for Sleep", "Instant Tingle Fix", "Whispered Bedtime Stories", "Binaural Beats ASMR",
    "Wooden Toy Sounds", "Paper Crinkling ASMR", "Fluffy Mic Triggers", "ASMR Glow Therapy"
]

CAPTIONS = [
    "Close your eyes and let the tingles take over.", "The perfect escape from a stressful day.",
    "Wear headphones for the best experience. 🎧", "Fall asleep in less than 5 minutes.",
    "Bringing you the most satisfying sounds on Earth.", "Your daily dose of pure relaxation.",
    "Let these sounds melt your brain. ✨", "Focus better with these calming triggers.",
    "Which trigger was your favorite? Let me know! 👇", "Healing your soul, one sound at a time.",
    "Gentle reminders to breathe and relax.", "Transform your night with deep sleep ASMR.",
    "Oddly satisfying visuals for a peaceful mind.", "Find your zen in this noisy world.",
    "Experience the ultimate brain massage.", "No talking, just pure tingly vibes.",
    "ASMR sounds that feel like a warm hug.", "Unlocking the secret to instant sleep.",
    "Satisfying your senses with every clip.", "Relax, recharge, and repeat.",
    "The science of tingles is here.", "Escaping reality with satisfying triggers.",
    "Sweet dreams start with these sounds.", "Experience binaural magic. 🌙",
    "Calm your anxiety instantly.", "Soft sounds for a loud world.",
    "Dive into a world of sensory bliss.", "Precision sounds for deep relaxation.",
    "Tingles that travel down your spine.", "Your bedtime routine just got better.",
    "Satisfyingly crisp and clean sounds.", "Mindful moments with ASMR.",
    "Unlock peace through your ears.", "The ultimate tingle challenge!",
    "Crunchy, soft, and everything in between.", "Rest your weary mind tonight.",
    "Tingly triggers you didn't know you needed."
]

# --- SEO & Insta Hashtags for USA/Global ASMR ---
# SEO Hashtags: Targeted for US Search & Discovery
SEO_HASHTAGS = "#ASMR #SleepAid #Relaxation #Satisfying #Tingles #OddlySatisfying #StressRelief #DeepSleep #ASMRCommunity #Mindfulness #Sensory #USA #TrendingVideo #BrainMassage"

# Insta SEO Hashtags: Top 5 Viral for Instagram Reels
INSTA_SEO_HASHTAGS = "#asmrvideo #satisfyingvideo #reelsusa #asmrtingles #explorepage"

# 1. History load & 15 days clean-up
history = {}
if os.path.exists(HISTORY_FILE):
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            history = data if isinstance(data, dict) else {}
    except:
        history = {}

now = datetime.now()
current_history = history.copy()

for vid, d_str in history.items():
    try:
        if (now - datetime.fromisoformat(d_str)).days >= 15:
            p = os.path.join(VIDEOS_DIR, vid)
            if os.path.exists(p): os.remove(p)
            if vid in current_history: del current_history[vid]
    except: pass

# 2. Pickup new video
if not os.path.exists(VIDEOS_DIR): os.makedirs(VIDEOS_DIR)
all_vids = [f for f in os.listdir(VIDEOS_DIR) if f.endswith('.mp4')]
new_video = next((v for v in all_vids if v not in current_history), None)

if not new_video:
    with open(HISTORY_FILE, 'w') as f: json.dump(current_history, f, indent=4)
    print("No new ASMR video found.")
    exit(0)

# 3. Random Selection
selected_title = random.choice(TITLES)
selected_caption = random.choice(CAPTIONS)

# 4. GitHub Raw Link
raw_video_link = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{VIDEOS_DIR}/{new_video}"

# 5. Telegram Posting Format (Requested Format)
tg_full_msg = (
    f"*{selected_title}*\n"
    f"{selected_caption}\n"
    ".\n"
    ".\n"
    ".\n"
    ".\n"
    f"{SEO_HASHTAGS}"
)

try:
    # Telegram Upload
    tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    with open(os.path.join(VIDEOS_DIR, new_video), 'rb') as f:
        requests.post(tg_url, data={'chat_id': CHAT_ID, 'caption': tg_full_msg, 'parse_mode': 'Markdown'}, files={'video': f})

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
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(current_history, f, indent=4)
    print(f"Success: Posted ASMR {new_video} for USA Audience")

except Exception as e:
    print(f"Error: {e}")
