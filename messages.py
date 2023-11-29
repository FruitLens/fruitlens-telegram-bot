START = """
Seja bem vindo ao bot de validação FruitLens! 🥳👏

Muito obrigado pelo seu tempo, você está nos ajudando a validar nosso projeto de TCC!

Para começar, envie uma imagem contendo uma fruta 🍎🍌🍊
"""

processing = "Processando..."

type_analysis_template = """Tipo: {}
Confiança: {:.2f}%
"""

stages_analysis_template = """Estágio de Maturação: {}
Confiança: {:.2f}%
"""

full_analysis__template = """{}
{}
"""

CONFIRMATION_BUTTON_YES = "Sim, concordo 👍"
CONFIRMATION_BUTTON_NO = "Não concordo 👎"

response_classes_translation = {
    "YES": CONFIRMATION_BUTTON_YES,
    "NO": CONFIRMATION_BUTTON_NO,
    "BANANA": "Banana 🍌",
    "ORANGE": "Laranja 🍊",
    "APPLE": "Maçã 🍎",
    "RAW": "Verde 😰",
    "UNRIPE": "Quase Maduro 😐",
    "OVERRIPE": "Bem Maduro 😏",
    "RIPE": "Maduro 🤩",
    "ROTTEN": "Podre 🤮",
}

THANKS_MESSAGE = "Obrigado pela resposta! 🙌"
AGREEMENT_QUESTION = "Você concorda com a classificação? 👆"
FRUIT_CLASSIFICATION_QUESTION = (
    "Qual a classificação ideal de fruta para a imagem enviada? 🙋"
)
STAGE_CLASSIFICATION_QUESTION = (
    "Qual a classificação ideal de estágio para a imagem enviada? 🙋"
)


def replace_response_classes_translation(old_message: str):
    message = old_message
    for old, new in response_classes_translation.items():
        message = message.replace(old, new)
    return message
