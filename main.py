import logging
import requests
import json

from telegram import Update
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from messages import (
    full_analysis__template,
    type_analysis_template,
    stages_analysis_template,
    processing,
    replace_classes_translation
)

URL = "http://0.0.0.0/predict/fruit"
TOKEN = ""

CONFIRMATION_BUTTON_YES = "Sim, concordo"
CONFIRMATION_BUTTON_NO = "Na verdade não"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def send_photo(file):
    payload = {}
    files = [("file", ("output.jpg", file, "image/jpeg"))]
    headers = {}

    response = requests.request("POST", URL, headers=headers, data=payload, files=files)

    return json.loads(response.text)


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = (
        update.message.photo[-1].file_id
        if len(update.message.photo) > 0
        else update.message.document.file_id
    )
    obj = await context.bot.get_file(file)

    analysis_result_dict = await send_photo(await obj.download_as_bytearray())

    await context.bot.send_message(chat_id=update.effective_chat.id, text=processing)

    message = ""
    if analysis_result_dict["type"]["name"] == "BANANA":
        _type = type_analysis_template.format(
            analysis_result_dict["type"]["name"],
            analysis_result_dict["type"]["confidence"],
        )
        stage = stages_analysis_template.format(
            analysis_result_dict["stage"]["name"],
            analysis_result_dict["stage"]["confidence"],
        )

        message = full_analysis__template.format(_type, stage)
    else:
        message = type_analysis_template.format(
            analysis_result_dict["type"]["name"],
            analysis_result_dict["type"]["confidence"],
        )

    message = replace_classes_translation(message)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


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


async def validate_classification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Você concorda com a classificação?"
    keyboard_reply = InlineKeyboardMarkup(
        # keyboard=[[CONFIRMATION_BUTTON_YES, CONFIRMATION_BUTTON_NO]],
        inline_keyboard=[
            [
                InlineKeyboardButton(CONFIRMATION_BUTTON_YES, callback_data="1"),
                InlineKeyboardButton(CONFIRMATION_BUTTON_NO, callback_data="2"),
            ]
        ],
        # resize_keyboard=True,
        # one_time_keyboard=True
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=message, reply_markup=keyboard_reply
    )


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    caps_handler = CommandHandler("caps", caps)
    photo_handler = MessageHandler(filters.PHOTO | filters.Document.IMAGE, photo)

    validation_handler = CommandHandler("val", validate_classification)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(caps_handler)
    application.add_handler(photo_handler)
    application.add_handler(validation_handler)

    application.run_polling()
