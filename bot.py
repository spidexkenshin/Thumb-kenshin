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


from PIL import Image, ImageDraw, ImageFont, ImageFilter

def round_corner(img, radius):

    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)

    draw.rounded_rectangle(
        [(0,0),(img.size[0],img.size[1])],
        radius=radius,
        fill=255
    )

    img.putalpha(mask)
    return img


def create_thumb(anime):

    W,H = 1920,1080

    bg = Image.open("bg.jpg").convert("RGB").resize((W,H))

    # cinematic blur
    bg = bg.filter(ImageFilter.GaussianBlur(8))

    canvas = Image.new("RGBA",(W,H))
    canvas.paste(bg,(0,0))

    overlay = Image.new("RGBA",(W,H),(0,0,0,90))
    canvas = Image.alpha_composite(canvas,overlay)

    # left character
    left = Image.open("left.png").convert("RGBA")
    left = left.resize((650,900))

    canvas.paste(left,(120,120),left)

    # right card
    right = Image.open("right.png").convert("RGBA")
    right = right.resize((450,650))

    card = Image.new("RGBA",(480,680),(20,20,20,220))
    card = round_corner(card,40)

    canvas.paste(card,(1320,200),card)

    right = round_corner(right,30)

    canvas.paste(right,(1335,215),right)

    draw = ImageDraw.Draw(canvas)

    font = ImageFont.truetype("assets/font.ttf",120)
    brand = ImageFont.truetype("assets/font.ttf",60)

    # anime title
    draw.text((960,880),anime,fill="white",font=font,anchor="mm")

    # branding
    draw.text((1700,1020),"KENSHIN ANIME",fill="white",font=brand)

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
