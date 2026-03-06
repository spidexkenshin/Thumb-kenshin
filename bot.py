import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from thumbnail import create_thumbnail
from io import BytesIO

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

users = {}

async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    users[update.effective_user.id] = {"step": "bg"}

    await update.message.reply_text("🎨 Send Background Image")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    if uid not in users:
        return

    step = users[uid]["step"]

    file = await update.message.photo[-1].get_file()
    img = await file.download_as_bytearray()

    if step == "bg":
        users[uid]["bg"] = img
        users[uid]["step"] = "right"
        await update.message.reply_text("📺 Send Right Thumbnail")

    elif step == "right":
        users[uid]["right"] = img
        users[uid]["step"] = "left"
        await update.message.reply_text("🧍 Send Left Character")

    elif step == "left":
        users[uid]["left"] = img
        users[uid]["step"] = "name"
        await update.message.reply_text("✍ Send Anime Name")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    if uid not in users:
        return

    if users[uid]["step"] != "name":
        return

    name = update.message.text

    bg = users[uid]["bg"]
    right = users[uid]["right"]
    left = users[uid]["left"]

    path = create_thumbnail(bg,right,left,name)

    await update.message.reply_photo(open(path,"rb"))

    del users[uid]

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("create",create))
app.add_handler(MessageHandler(filters.PHOTO,handle_photo))
app.add_handler(MessageHandler(filters.TEXT,handle_text))

app.run_polling()
