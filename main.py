import logging
import requests
import json
from ClassificationEnums import FruitType, FruitStage, Confirmation
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler
)

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update

from messages import (
    full_analysis__template,
    type_analysis_template,
    stages_analysis_template,
    processing,
    replace_classes_translation
)
URL = "http://0.0.0.0"
PREDICT = "/predict/fruit"
SAVE_S3 = "/upload"
URL_BUCKET = "fruit-lens-dream-team-training-data"
TOKEN = ""

CONFIRMATION_BUTTON_YES = "Sim, concordo"
CONFIRMATION_BUTTON_NO = "Na verdade não"

temp_fruit_selection = ""

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def send_photo(file):
    payload = {}
    files = [("file", ("output.jpg", file, "image/jpeg"))]
    headers = {}

    response = requests.request("POST", URL + PREDICT, headers=headers, data=payload, files=files)

    return json.loads(response.text)

async def save_photo(file, file_name, file_id, chat_id):
    payload = {}
    files = [("file", ("output.jpg", file, "image/jpeg")),
             ("file_name", file_name),
             ("file_id", file_id),
             ("chat_id", chat_id)]
    headers = {}

    response = requests.request("POST", URL + SAVE_S3 + f"?file_name={files[1][-1]}&file_id={[2][-1]}&chat_id={[3][-1]}",
        headers=headers,
        data=payload,
        files=files
    )

    print(response)

    return json.loads(response.text)


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = (
        update.message.photo[-1].file_id
        if len(update.message.photo) > 0
        else update.message.document.file_id
    )
    obj = await context.bot.get_file(file)

    file = await obj.download_as_bytearray()
    analysis_result_dict = await send_photo(file)

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
    # await save_photo(
    #     file,
    #     f'{update.effective_chat.id}_{analysis_result_dict["type"]["name"]}.jpeg',
    #     update.message.photo[-1].file_id,
    #     update.effective_chat.id
    # )
    # ,  update.message.photo[-1].file_id
    temp_fruit_selection = analysis_result_dict["type"]["name"]
    await validate_classification(update, context)


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
        inline_keyboard=[
            [
                InlineKeyboardButton(CONFIRMATION_BUTTON_YES, callback_data=Confirmation.YES.value),
                InlineKeyboardButton(CONFIRMATION_BUTTON_NO, callback_data=Confirmation.NO.value)
            ]
        ]
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=message, reply_markup=keyboard_reply
    )

async def select_fruit_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Qual a classificação ideal de fruta para a imagem enviada?"
    keyboard_reply = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("Banana", callback_data=FruitType.BANANA.value),
                InlineKeyboardButton("Maça", callback_data=FruitType.APPLE.value),
                InlineKeyboardButton("Laranja", callback_data=FruitType.ORANGE.value),
            ]
        ]
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=message, reply_markup=keyboard_reply
    )

async def select_fruit_stage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Qual a classificação ideal de estágio para a imagem enviada?"
    keyboard_reply = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("Verde", callback_data=FruitStage.RAM.value)],
            [InlineKeyboardButton("Quase maduro", callback_data=FruitStage.UNRIPE.value)],
            [InlineKeyboardButton("Maduro", callback_data=FruitStage.RIPE.value)],
            [InlineKeyboardButton("Passado", callback_data=FruitStage.OVERRIPE.value)],
            [InlineKeyboardButton("Podre", callback_data=FruitStage.ROTTEN.value)]
        ]
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=message, reply_markup=keyboard_reply
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
        
    if  query.data in [member.value for member in Confirmation]:
        # validação do caso de conf
        print("[FRUIT-LENS][CLASSIFICATION] - Validação com a classificação do usuário")
        await validate_confirm_reponse(update, context, query.data)
    elif query.data in [member.value for member in FruitType]:
        print("[FRUIT-LENS][FRUIT-TYPE] - Seleção da fruta do usuário")
        await validate_fruit_type(update, context, query.data)
    elif query.data in [member.value for member in FruitStage]:
        print("[FRUIT-LENS][FRUIT-TYPE] - Seleção da fruta do usuário")
        await validate_fruit_stage(update, context, query.data)
    else:
        print(query.data)

async def send_message(context: ContextTypes.DEFAULT_TYPE, chat_id, message):
    await context.bot.send_message(chat_id=chat_id, text=message)

async def validate_confirm_reponse(update: Update, context: ContextTypes.DEFAULT_TYPE, response: Confirmation):
    if response == Confirmation.YES:
        #  await query.edit_message_text(text=f"Qual seria a classificação ideal?")
        await send_message(context, chat_id=update.effective_chat.id, message="Obrigado pelo feedback")
        # TODO: Código para confirmar predição do usuário
    else:
        await select_fruit_options(update, context)

async def validate_fruit_type(update: Update, context: ContextTypes.DEFAULT_TYPE, response: FruitType):
    print(temp_fruit_selection)
    print(response)
    if response == FruitType.BANANA and response == temp_fruit_selection:
        # Salvar fruta
        await select_fruit_stage(update, context)
    elif response == temp_fruit_selection:
        await send_message(context, update.effective_chat.id, message="Nós acertamos e você que errou, vacilão!")
    else:
        await send_message(context, update.effective_chat.id, message="Obrigado pela resposta meu irmão!")
        #Pegar mensagem
        #Enviar dados para o back a resposta do usuário

async def validate_fruit_stage(update: Update, context: ContextTypes.DEFAULT_TYPE, response: FruitStage):
    #Salvar no back a os dados
    await send_message(context, update.effective_chat.id, message="Valeu meu irmão!")
    

if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    caps_handler = CommandHandler("caps", caps)
    photo_handler = MessageHandler(filters.PHOTO | filters.Document.IMAGE, photo)

    validation_handler = CommandHandler("val", validate_classification)

    application.add_handler(CallbackQueryHandler(callback_handler))

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(caps_handler)
    application.add_handler(photo_handler)
    application.add_handler(validation_handler)

    application.run_polling()