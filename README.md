# 🎌 Kenshin Anime Thumbnail Bot

Telegram bot jo anime thumbnails automatically generate karta hai — exactly waise jaise
**@KENSHIN_ANIME** channel pe hote hain.

---

## ✨ Features

- **3-step image flow** — background → right panel → left character
- **Auto layout** — phone mockup + anime panel + buttons sab automatic
- **Dark overlay** right panel pe automatic lagta hai
- **Blurred & darkened background** auto generate hota hai
- **Bebas Neue font** (anime-style bold) auto download hoti hai
- **Admin-only** — sirf allowed users use kar sakte hain
- **Railway ready** — ek click deploy

---

## 📸 Output Layout

```
┌────────────────────────────────────────────────────────┐
│  ┌──────────┐  ┌──────────────────────────────────┐   │
│  │          │  │  ANIME TITLE               ░░░░░ │   │
│  │  Phone   │  │  KENSHIN ANIME                   │   │
│  │ Mockup   │  │           [Anime Artwork]         │   │
│  │ (Left    │  │                                   │   │
│  │  Image)  │  └──────────────────────────────────┘   │
│  └──────────┘                                          │
│              [ WATCH NOW ]  [ KENSHIN ANIME ]          │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 Setup

### Step 1 — Telegram Credentials

1. **API ID & Hash** → [my.telegram.org](https://my.telegram.org)
2. **Bot Token** → [@BotFather](https://t.me/BotFather) pe `/newbot`
3. **Your User ID** → [@userinfobot](https://t.me/userinfobot) se pata karo

---

### Step 2 — Railway Deployment (Recommended)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app)

1. GitHub pe repo fork karo (ya naya repo banao, files upload karo)
2. [railway.app](https://railway.app) pe jao → **New Project → Deploy from GitHub**
3. Repo select karo
4. **Variables** tab mein yeh set karo:

| Variable    | Value                        |
|-------------|------------------------------|
| `API_ID`    | Apna API ID (number)         |
| `API_HASH`  | Apna API Hash (string)       |
| `BOT_TOKEN` | @BotFather se mila token     |
| `ADMIN_IDS` | Tera Telegram ID (number)    |

5. Deploy! ✅  Bot khud start ho jayega.

---

### Step 3 — Local Setup (Optional)

```bash
pip install -r requirements.txt
python setup_font.py          # Bebas Neue font download karo

# .env file banao
cp .env.example .env
# .env open karo aur values fill karo

python bot.py
```

---

## 📖 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Bot ka intro |
| `/create <anime name>` | Thumbnail banana shuru karo |
| `/cancel` | Current session band karo |
| `/status` | Current session ka status dekho |

---

## 🖼️ Step-by-Step Flow

```
You: /create Jujutsu Kaisen

Bot: ✅ Anime: Jujutsu Kaisen
     📸 Step 1/3 — Background Image bhejo

You: [sends background image]

Bot: ✅ Background mila!
     🖼️ Step 2/3 — Right Panel Image bhejo

You: [sends anime poster/key visual]

Bot: ✅ Right panel mila!
     📱 Step 3/3 — Left Character Image bhejo

You: [sends character wallpaper]

Bot: ⏳ Thumbnail ban raha hai...
Bot: [sends final thumbnail image] ✅
```

---

## 📁 File Structure

```
KenshinThumbnailBot/
├── bot.py            ← Main bot (commands, state machine)
├── thumbnail.py      ← PIL image composition engine
├── setup_font.py     ← Bebas Neue font downloader
├── requirements.txt
├── Procfile          ← Railway start command
├── railway.toml      ← Railway config
├── .env.example      ← Environment variables template
├── .gitignore
└── README.md
```

---

## 💡 Tips

- **Background image**: Anime ka koi bhi dramatic scene ya wallpaper — blur auto lagta hai
- **Right panel**: Official anime poster / key visual best lagta hai
- **Left image**: Character ka portrait / phone wallpaper — tall images better dikhti hain
- **Anime name** jo likha woh thumbnail pe UPPERCASE mein aayega

---

## 📢 Channels

- Anime → **@KENSHIN_ANIME**
- Manhwa → **@MANWHA_VERSE**
