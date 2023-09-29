start = """
Bem vindo ao bot de validação do FruitLens. Muito obrigado pelo seu tempo nos ajudando a validar nosso projeto de TCC!
Por favor, nos envie aqui no chat uma foto de uma banana ou de um cacho de bananas. Você pode usar a câmera ou escolher uma foto da galeria.

Considerando a seguinte classificação:
Verde: bananas que possuem ainda alguns traços verdes
Madura: bananas amarelas ou com algumas manchas pretas, mas ainda bom estado para consumo.
Podre: bananas que estão majoritariamente pretas ou possuem alguma deformidade causada por algum fator externo e não podem ser consumidas

Você concorda com o resultado da classificação?
0 - Não
1 - Sim

(caso não)
Qual classificação você acha que seria mais adequada? digite:
0 para Verde
1 para Madura
2 para Podre

Obrigado pela contribuição!
Quer enviar outra foto?
0 - Não, quero encerrar
1 - Sim, quero outra
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


def replace_classes_translation(old_message: str):
    message = old_message
    for old, new in classes_translation.items():
        message = message.replace(old, new)
    return message


classes_translation = {
    "BANANA": "Banana 🍌",
    "ORANGE": "Laranja 🍊",
    "APPLE": "Maçã 🍎",
    "RAW": "Verde 😰",
    "OVERRIPE": "Podre 🤮",
    "RIPE": "Maduro 🤩",
}

CONFIRMATION_BUTTON_YES = "Sim, concordo "
CONFIRMATION_BUTTON_NO = "Na verdade não"

reponse_classes_translation = {
    "YES": CONFIRMATION_BUTTON_YES,
    "NO": CONFIRMATION_BUTTON_NO,
    "BANANA": "Banana 🍌",
    "ORANGE": "Laranja 🍊",
    "APPLE": "Maçã 🍎",
    "RAW": "Verde 😐",
    "UNRIPE": "Quase Maduro😏",
    "OVERRIPE": "Bem Maduro 😳",
    "RIPE": "Maduro🤩",
    "ROTTEN": "Podre 🤢",
}

THANKS_MESSAGE = "Obrigado pela resposta! 👍🙌"
AGREEMENT_QUESTION = "Você concorda com a classificação? 👆🏻"
FRUIT_CLASSIFICATION_QUESTION = "Qual a classificação ideal de fruta para a imagem enviada?"
STAGE_CLASSIFICATION_QUESTION = "Qual a classificação ideal de estágio para a imagem enviada?"


def replace_reponse_classes_translation(old_message: str):
    message = old_message
    for old, new in reponse_classes_translation.items():
        message = message.replace(old, new)
    return message
