import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image, ImageDraw, ImageFont

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

FONT_PATH = "assets/font.ttf"

THUMB_WIDTH = 1920
THUMB_HEIGHT = 1080

user_data = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text("🔥 Kenshin Anime Thumbnail Bot Ready!")


async def create_thumbnail(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    user_data[update.effective_user.id] = {"step": 1}

    await update.message.reply_text("Send Anime Name")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        return

    if user_id not in user_data:
        return

    data = user_data[user_id]

    # STEP 1 → Anime Name
    if data["step"] == 1:

        data["anime"] = update.message.text
        data["step"] = 2

        await update.message.reply_text("Send Background Image")


    # STEP 2 → Background
    elif data["step"] == 2:

        photo = await update.message.photo[-1].get_file()
        await photo.download_to_drive("bg.jpg")

        data["step"] = 3

        await update.message.reply_text("Send LEFT Character Image (PNG recommended)")


    # STEP 3 → Left Character
    elif data["step"] == 3:

        photo = await update.message.photo[-1].get_file()
        await photo.download_to_drive("left.png")

        data["step"] = 4

        await update.message.reply_text("Send RIGHT Thumbnail Image")


    # STEP 4 → Right Image
    elif data["step"] == 4:

        photo = await update.message.photo[-1].get_file()
        await photo.download_to_drive("right.png")

        anime_name = data["anime"]

        create_thumb(anime_name)

        await update.message.reply_photo(photo=open("thumbnail.png", "rb"))

        user_data.pop(user_id)


def create_thumb(anime):

    # Background
    bg = Image.open("bg.jpg").convert("RGBA").resize((THUMB_WIDTH, THUMB_HEIGHT))

    # Left Character
    left = Image.open("left.png").convert("RGBA").resize((700, 900))

    # Right Image
    right = Image.open("right.png").convert("RGBA").resize((500, 700))

    canvas = bg.copy()

    # Dark overlay
    overlay = Image.new("RGBA", (THUMB_WIDTH, THUMB_HEIGHT), (0, 0, 0, 120))
    canvas = Image.alpha_composite(canvas, overlay)

    # Paste Left Character
    canvas.paste(left, (100, 150), left)

    # Right side black transparent box
    black_box = Image.new("RGBA", (520, 720), (0, 0, 0, 150))
    canvas.paste(black_box, (1280, 180), black_box)

    # Paste Right Image
    canvas.paste(right, (1300, 200), right)

    draw = ImageDraw.Draw(canvas)

    # Fonts
    font = ImageFont.truetype(FONT_PATH, 120)
    brand_font = ImageFont.truetype(FONT_PATH, 60)

    # Anime Title
    draw.text((960, 900), anime, fill="white", font=font, anchor="mm")

    # Branding
    draw.text((1650, 1020), "KENSHIN ANIME", fill="white", font=brand_font)

    canvas = canvas.convert("RGB")

    canvas.save("thumbnail.png")


def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create_thumbnail", create_thumbnail))

    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))

    print("Bot Running...")

    app.run_polling()


if __name__ == "__main__":
    main()
