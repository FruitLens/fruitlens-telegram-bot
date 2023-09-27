import logging
from Handler import Handler
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)
from telegram import Update
from messages import CONFIRMATION_BUTTON_YES, CONFIRMATION_BUTTON_NO
from constants import TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    if (
        update.message.text == CONFIRMATION_BUTTON_YES
        or update.message.text == CONFIRMATION_BUTTON_NO
    ):
        message = "Obrigado pela contribuição!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = " ".join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


if __name__ == "__main__":
    handler = Handler()
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    caps_handler = CommandHandler("caps", caps)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    photo_handler = MessageHandler(
        filters.PHOTO | filters.Document.IMAGE, handler.receive_photo
    )

    application.add_handler(CallbackQueryHandler(handler.callback_handler))

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(caps_handler)
    application.add_handler(photo_handler)

    application.run_polling()
