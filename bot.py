import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image, ImageDraw, ImageFont

from config import BOT_TOKEN, ADMIN_ID, FONT_PATH, THUMB_WIDTH, THUMB_HEIGHT

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

    if data["step"] == 1:

        data["anime"] = update.message.text
        data["step"] = 2

        await update.message.reply_text("Send Background Image")

    elif data["step"] == 2:

        photo = await update.message.photo[-1].get_file()
        await photo.download_to_drive("bg.jpg")

        data["step"] = 3

        await update.message.reply_text("Send LEFT Character Image")

    elif data["step"] == 3:

        photo = await update.message.photo[-1].get_file()
        await photo.download_to_drive("left.png")

        data["step"] = 4

        await update.message.reply_text("Send RIGHT Thumbnail Image")

    elif data["step"] == 4:

        photo = await update.message.photo[-1].get_file()
        await photo.download_to_drive("right.png")

        anime_name = data["anime"]

        create_thumb(anime_name)

        await update.message.reply_photo(photo=open("thumbnail.png","rb"))

        user_data.pop(user_id)

def create_thumb(anime):

    bg = Image.open("bg.jpg").resize((THUMB_WIDTH, THUMB_HEIGHT))
    left = Image.open("left.png").resize((700,900))
    right = Image.open("right.png").resize((500,700))

    canvas = bg.convert("RGBA")

    overlay = Image.new("RGBA",(THUMB_WIDTH,THUMB_HEIGHT),(0,0,0,120))
    canvas = Image.alpha_composite(canvas, overlay)

    canvas.paste(left,(100,150),left)
    canvas.paste(right,(1300,200),right)

    draw = ImageDraw.Draw(canvas)

    font = ImageFont.truetype(FONT_PATH,120)
    brand_font = ImageFont.truetype(FONT_PATH,60)

    draw.text((900,850),anime,fill="white",font=font,anchor="mm")

    draw.text((1600,1000),"KENSHIN ANIME",fill="white",font=brand_font)

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
