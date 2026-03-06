"""
Kenshin Anime Thumbnail Bot
─────────────────────────────
Admin sends /create <anime name>
Bot collects 3 images step-by-step → generates thumbnail → sends back
"""

import os
import io
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from thumbnail import create_thumbnail

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
API_ID    = int(os.environ["API_ID"])
API_HASH  = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_IDS = set(
    int(x.strip()) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip()
)

# ── State keys ────────────────────────────────────────────────────────────────
WAIT_BG    = "wait_bg"
WAIT_RIGHT = "wait_right"
WAIT_LEFT  = "wait_left"

# user_id → {step, anime_name, bg, right, left}
sessions: dict[int, dict] = {}

# ── Client ────────────────────────────────────────────────────────────────────
app = Client(
    "kenshin_thumb_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# ── Helpers ───────────────────────────────────────────────────────────────────
def is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS


async def download_photo(msg: Message) -> bytes:
    buf = await msg.download(in_memory=True)
    buf.seek(0)
    return buf.read()


# ── Handlers ─────────────────────────────────────────────────────────────────
@app.on_message(filters.command("start") & filters.private)
async def cmd_start(client: Client, msg: Message):
    await msg.reply_text(
        "🎌 **Kenshin Anime Thumbnail Bot**\n\n"
        "Yeh bot anime thumbnails banata hai exactly waise\n"
        "jaise @KENSHIN_ANIME channel pe hote hain.\n\n"
        "**Usage (Admin only):**\n"
        "`/create <anime name>`\n\n"
        "**Example:**\n"
        "`/create Jujutsu Kaisen`\n\n"
        "Bot 3 images maangega — fir seconds mein thumbnail ready! ⚡"
    )


@app.on_message(filters.command("create") & filters.private)
async def cmd_create(client: Client, msg: Message):
    if not is_admin(msg.from_user.id):
        return await msg.reply_text("❌ Sirf admins use kar sakte hain!")

    anime_name = " ".join(msg.command[1:]).strip()
    if not anime_name:
        return await msg.reply_text(
            "❌ Anime ka naam likhna bhool gaye!\n"
            "**Example:** `/create Jujutsu Kaisen`"
        )

    sessions[msg.from_user.id] = {
        "step":       WAIT_BG,
        "anime_name": anime_name,
        "bg":         None,
        "right":      None,
        "left":       None,
    }

    await msg.reply_text(
        f"✅ Anime: **{anime_name}**\n\n"
        f"📸 **Step 1 / 3 — Background Image**\n"
        f"Thumbnail ka full background image send karo.\n"
        f"_(Any anime image — blurred effect automatically lagega)_\n\n"
        f"_/cancel karo agar chodna ho._"
    )


@app.on_message(filters.command("cancel") & filters.private)
async def cmd_cancel(client: Client, msg: Message):
    if msg.from_user.id in sessions:
        sessions.pop(msg.from_user.id)
        await msg.reply_text("❌ Cancelled. Phir se `/create` karo jab ready ho.")
    else:
        await msg.reply_text("Koi active session nahi hai.")


@app.on_message(filters.command("status") & filters.private)
async def cmd_status(client: Client, msg: Message):
    if not is_admin(msg.from_user.id):
        return
    s = sessions.get(msg.from_user.id)
    if not s:
        await msg.reply_text("Koi active session nahi hai. `/create` se shuru karo.")
    else:
        step_map = {
            WAIT_BG:    "Waiting for background image",
            WAIT_RIGHT: "Waiting for right panel image",
            WAIT_LEFT:  "Waiting for left character image",
        }
        await msg.reply_text(
            f"📋 **Current Session**\n"
            f"Anime: {s['anime_name']}\n"
            f"Step: {step_map.get(s['step'], s['step'])}"
        )


@app.on_message(filters.photo & filters.private)
async def handle_photo(client: Client, msg: Message):
    uid = msg.from_user.id
    if not is_admin(uid):
        return

    s = sessions.get(uid)
    if not s:
        # Not in a session — ignore photo
        return

    step = s["step"]
    img_bytes = await download_photo(msg)

    # ── Step 1: Background ────────────────────────────────────────────────────
    if step == WAIT_BG:
        s["bg"]   = img_bytes
        s["step"] = WAIT_RIGHT
        await msg.reply_text(
            "✅ Background image mila!\n\n"
            "🖼️ **Step 2 / 3 — Right Panel Image**\n"
            "Right side ka anime poster / key visual send karo.\n"
            "_(Yeh right wala bada panel hoga)_"
        )

    # ── Step 2: Right panel ───────────────────────────────────────────────────
    elif step == WAIT_RIGHT:
        s["right"] = img_bytes
        s["step"]  = WAIT_LEFT
        await msg.reply_text(
            "✅ Right panel image mila!\n\n"
            "📱 **Step 3 / 3 — Left Character Image**\n"
            "Left phone mockup wali character/wallpaper image send karo.\n"
            "_(Portrait orientation best lagti hai)_"
        )

    # ── Step 3: Left character → Generate! ───────────────────────────────────
    elif step == WAIT_LEFT:
        s["left"] = img_bytes
        sessions.pop(uid)  # Clear session

        proc = await msg.reply_text("⏳ Thumbnail ban raha hai... thoda wait karo!")

        try:
            thumb_buf = create_thumbnail(
                anime_name = s["anime_name"],
                bg_bytes   = s["bg"],
                right_bytes= s["right"],
                left_bytes = s["left"],
            )

            await proc.delete()
            await msg.reply_photo(
                photo   = thumb_buf,
                caption = (
                    f"✅ **{s['anime_name']}** Thumbnail Ready!\n\n"
                    f"📢 @KENSHIN_ANIME | 📖 @MANWHA_VERSE"
                ),
            )
            log.info(f"Thumbnail created for: {s['anime_name']}")

        except Exception as e:
            log.error(f"Thumbnail error: {e}", exc_info=True)
            await proc.edit_text(
                f"❌ Kuch error aa gaya:\n`{e}`\n\n"
                "Dobara `/create` se try karo."
            )


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log.info("🚀 Kenshin Thumbnail Bot starting...")
    app.run()
