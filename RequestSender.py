import requests
import json
from messages import (
    full_analysis__template,
    type_analysis_template,
    stages_analysis_template,
)


class RequestSenderService:
    def define_predict_reponse_obj(self, fruit_dic):
        message = ""
        if fruit_dic["type"]["name"] == "BANANA":
            _type = type_analysis_template.format(
                fruit_dic["type"]["name"],
                fruit_dic["type"]["confidence"],
            )
            stage = stages_analysis_template.format(
                fruit_dic["stage"]["name"],
                fruit_dic["stage"]["confidence"],
            )

            message = full_analysis__template.format(_type, stage)

        else:
            message = type_analysis_template.format(
                fruit_dic["type"]["name"],
                fruit_dic["type"]["confidence"],
            )

        return message

    async def send_request(self, url, payload, headers, files, method):
        response = requests.request(
            method, url, headers=headers, data=payload, files=files
        )
        return json.loads(response.text)
