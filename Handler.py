import time 
from RequestSender import RequestSenderService
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext
)

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from messages import (
    processing,
    CONFIRMATION_BUTTON_YES,
    CONFIRMATION_BUTTON_NO,
    replace_classes_translation
)
from constants import BASE_URL, PREDICT
from ClassificationEnums import FruitType, FruitStage, Confirmation

class Handler:
    temp_fruit_selection = ""
    temp_stage_selections = ""
    def __init__(self):
        pass

    async def receive_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        sender = RequestSenderService()
        file = (
            update.message.photo[-1].file_id
            if len(update.message.photo) > 0
            else update.message.document.file_id
        )
        obj = await context.bot.get_file(file)

        file = await obj.download_as_bytearray()

        analysis_result_dict = await sender.send_request(
            BASE_URL + PREDICT,
            {},
            {},
            [("file", ("output.jpg", file, "image/jpeg"))],
            "POST"
        )

        await context.bot.send_message(chat_id=update.effective_chat.id, text=processing)
        self.temp_fruit_selection = analysis_result_dict["type"]["name"]
        if (self.temp_fruit_selection) == FruitType.BANANA.value:
            self.temp_stage_selections = analysis_result_dict["stage"]["name"]

        message = replace_classes_translation(
            sender.define_predict_reponse_obj(analysis_result_dict)
        )

        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        await self.validate_classification(update, context)

    async def validate_classification(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    async def callback_handler(self, update: Update, context: CallbackContext):
        query = update.callback_query
        await query.answer()
        # Aqui removemos os botões para o usuário não responder novamente
        await context.bot.edit_message_reply_markup(
            chat_id=query.message.chat_id, message_id=query.message.message_id, reply_markup=None
        )

        if  query.data in [member.value for member in Confirmation]:
            # validação do caso de conf
            print("[FRUIT-LENS][CLASSIFICATION] - Validação com a classificação do usuário")
            await self.validate_confirm_reponse(update, context, query.data)
        elif query.data in [member.value for member in FruitType]:
            print("[FRUIT-LENS][FRUIT-TYPE] - Seleção da fruta do usuário")
            await self.validate_fruit_type(update, context, query.data)
        elif query.data in [member.value for member in FruitStage]:
            print("[FRUIT-LENS][FRUIT-TYPE] - Seleção da fruta do usuário")
            await self.validate_fruit_stage(update, context, query.data)
        else:
            print(query.data)

    async def send_message(self, context: ContextTypes.DEFAULT_TYPE, chat_id, message):
        await context.bot.send_message(chat_id=chat_id, text=message)

    async def validate_confirm_reponse(self, update: Update, context: ContextTypes.DEFAULT_TYPE, response: Confirmation):
        print(response)
        if response == Confirmation.YES.value:
            #  await query.edit_message_text(text=f"Qual seria a classificação ideal?")
            await self.send_message(context, chat_id=update.effective_chat.id, message="Obrigado pelo feedback")
            # TODO: Código para confirmar predição do usuário
        else:
            await self.select_fruit_options(update, context)

    async def select_fruit_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    async def select_fruit_stage(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    async def validate_fruit_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE, response: FruitType):
        print(response)
        print(self.temp_fruit_selection)
        if response == FruitType.BANANA.value and response == self.temp_fruit_selection:
            # Salvar fruta
            await self.select_fruit_stage(update, context)
        elif response == self.temp_fruit_selection:
            await self.send_message(context, update.effective_chat.id, message="Nós acertamos e você que errou, vacilão!")
        else:
            await self.send_message(context, update.effective_chat.id, message="Obrigado pela resposta meu irmão!")
            #Pegar mensagem
            #Enviar dados para o back a resposta do usuário

    async def validate_fruit_stage(self, update: Update, context: ContextTypes.DEFAULT_TYPE, response: FruitStage):
        if (response == self.temp_stage_selections):
            await self.send_message(context, update.effective_chat.id, message="Estagio foi correto!")
        else:
            #Salvar no back a os dados
            await self.send_message(context, update.effective_chat.id, message="Valeu meu irmão!")