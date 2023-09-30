import time
import json
from RequestSender import RequestSenderService
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from messages import (
    processing,
    CONFIRMATION_BUTTON_YES,
    CONFIRMATION_BUTTON_NO,
    replace_classes_translation,
    replace_reponse_classes_translation,
    AGREEMENT_QUESTION,
    THANKS_MESSAGE,
    FRUIT_CLASSIFICATION_QUESTION,
    STAGE_CLASSIFICATION_QUESTION
)
from constants import BASE_URL, PREDICT_URI, FEEDBACK_TEMP, KEY, FEEDBACK_URI
from ClassificationEnums import FruitType, FruitStage, Confirmation


class Handler:

    sender = RequestSenderService()
    def __init__(self):
        pass

    async def receive_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        file_id = (
            update.message.photo[-1].file_id
            if len(update.message.photo) > 0
            else update.message.document.file_id
        )
        obj = await context.bot.get_file(file_id)

        file = await obj.download_as_bytearray()

        print({'telegram_img_id': file_id, 'telegram_conversation_id': update.message.chat_id})
        analysis_result_dict = await self.sender.send_request(
            BASE_URL + PREDICT_URI,
            {'telegram_img_id': file_id, 'telegram_conversation_id': update.message.chat_id},
            {},
            [("file", ("output.jpg", file, "image/jpeg"))],
            "POST",
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=processing
        )
        FEEDBACK_TEMP['model_type'] = analysis_result_dict["type"]["name"]
        FEEDBACK_TEMP['img_id'] = file_id

        context.chat_data[KEY] = FEEDBACK_TEMP
        if (analysis_result_dict["type"]["name"]) == FruitType.BANANA.value:
            FEEDBACK_TEMP['model_stage'] = analysis_result_dict["maturation_stage"]["name"]
            context.chat_data[KEY] = FEEDBACK_TEMP

        message = replace_classes_translation(
            self.sender.define_predict_reponse_obj(analysis_result_dict)
        )

        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        await self.validate_classification(update, context)

    async def validate_classification(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        keyboard_reply = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        CONFIRMATION_BUTTON_YES, callback_data=Confirmation.YES.value
                    ),
                    InlineKeyboardButton(
                        CONFIRMATION_BUTTON_NO, callback_data=Confirmation.NO.value
                    ),
                ]
            ]
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=AGREEMENT_QUESTION, reply_markup=keyboard_reply
        )

    async def callback_handler(self, update: Update, context: CallbackContext):
        query = update.callback_query
        await query.answer()

        # Aqui removemos os botões para o usuário não responder novamente
        await context.bot.edit_message_reply_markup(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup=None,
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Sua resposta foi: {replace_reponse_classes_translation(query.data)}",
        )

        if query.data in [member.value for member in Confirmation]:
            # validação do caso de conf
            print(
                "[FRUIT-LENS][CLASSIFICATION] - Validação com a classificação do usuário"
            )
            await self.validate_confirm_reponse(update, context, query.data)
        elif query.data in [member.value for member in FruitType]:
            print("[FRUIT-LENS][FRUIT-TYPE] - Seleção de tipo de fruta do usuario")
            await self.validate_fruit_type(update, context, query.data)
        elif query.data in [member.value for member in FruitStage]:
            print("[FRUIT-LENS][FRUIT-MATURATION-STAGE] - Seleção de estagio de maturacao de fruta do usuario")
            await self.validate_fruit_stage(update, context, query.data)
        else:
            print(query.data)

    async def send_message(self, context: ContextTypes.DEFAULT_TYPE, chat_id, message):
        await context.bot.send_message(chat_id=chat_id, text=message)

    async def validate_confirm_reponse(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, response: Confirmation
    ):
        print(response)
        if response == Confirmation.YES.value:
            #  await query.edit_message_text(text=f"Qual seria a classificação ideal?")
            await self.send_message(
                context,
                chat_id=update.effective_chat.id,
                message=THANKS_MESSAGE,
            )
            chat_data = context.chat_data.get(KEY, 'Not found')
            payload = {"user_class_fruit_type": "NONE", "user_class_maturation_stage": "NONE", "user_approval": True}
            response = await self.sender.send_request(
                BASE_URL + FEEDBACK_URI + f'/{chat_data["img_id"]}',
                json.dumps(payload, indent = 4),
                {},
                [],
                "PUT",
            )
            print(response)

        else:
            await self.select_fruit_options(update, context)

    async def select_fruit_options(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        keyboard_reply = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        "Banana", callback_data=FruitType.BANANA.value
                    ),
                    InlineKeyboardButton("Maça", callback_data=FruitType.APPLE.value),
                    InlineKeyboardButton(
                        "Laranja", callback_data=FruitType.ORANGE.value
                    ),
                ]
            ]
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=FRUIT_CLASSIFICATION_QUESTION, reply_markup=keyboard_reply
        )

    async def select_fruit_stage(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        keyboard_reply = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("Verde 😐", callback_data=FruitStage.RAM.value)],
                [
                    InlineKeyboardButton(
                        "Quase maduro", callback_data=FruitStage.UNRIPE.value
                    )
                ],
                [InlineKeyboardButton("Maduro", callback_data=FruitStage.RIPE.value)],
                [
                    InlineKeyboardButton(
                        "Bem maduro", callback_data=FruitStage.OVERRIPE.value
                    )
                ],
                [InlineKeyboardButton("Podre", callback_data=FruitStage.ROTTEN.value)],
            ]
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=STAGE_CLASSIFICATION_QUESTION, reply_markup=keyboard_reply
        )

    async def validate_fruit_type(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, response: FruitType
    ):
        fruit_selection = context.chat_data.get(KEY, 'Not found')
        print(response)
        if response == FruitType.BANANA.value and response == fruit_selection['model_type']:
            # Salvar fruta
            FEEDBACK_TEMP['user_type'] = response
            context.chat_data[KEY] = FEEDBACK_TEMP
            await self.select_fruit_stage(update, context)
        elif response == fruit_selection:
            await self.send_message(
                context,
                update.effective_chat.id,
                message=THANKS_MESSAGE,
            )
        else:
            await self.send_message(
                context, update.effective_chat.id, message=STAGE_CLASSIFICATION_QUESTION
            )
            # Pegar mensagem
            # Enviar dados para o back a resposta do usuário

    async def validate_fruit_stage(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, response: FruitStage
    ):
        stage_selection = context.chat_data.get(KEY, 'Not found')
        if response == stage_selection['model_stage']:
            await self.send_message(
                context, update.effective_chat.id, message=THANKS_MESSAGE
            )
        else:
            # Salvar no back a os dados
            await self.send_message(
                context, update.effective_chat.id, message=THANKS_MESSAGE
            )
