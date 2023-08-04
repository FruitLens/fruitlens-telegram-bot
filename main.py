import logging
import requests
import json

from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

URL = "URL"
TOKEN = 'TOKEN'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def send_photo(file):
    payload = {}
    files = [
        ('file', ('output.jpg', file, 'image/jpeg'))
    ]
    headers = {}

    response = requests.request("POST", URL, headers=headers, data=payload, files=files)

    return json.loads(response.text)


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.photo[-1].file_id if len(update.message.photo) > 0 else update.message.document.file_id
    obj = await context.bot.get_file(file)

    res = await send_photo(await obj.download_as_bytearray())

    print(res)

    await context.bot.send_message(chat_id=update.effective_chat.id, text='That\'s an image!')
    await context.bot.send_message(chat_id=update.effective_chat.id, text=json.dumps(res))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    caps_handler = CommandHandler('caps', caps)
    photo_handler = MessageHandler(
        filters.PHOTO | filters.Document.IMAGE,
        photo
    )

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(caps_handler)
    application.add_handler(photo_handler)

    application.run_polling()
