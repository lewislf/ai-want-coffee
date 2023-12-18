from typing import List
from openai import Client
from image import encode_image


class GPTAgent():

    history: List
    model: str

    def __init__(self, system_prompt: str, model: str) -> None:
        self.history = []
        self.model = model
        self.add_system_prompt(system_prompt)

    def add_system_prompt(self, system_prompt: str):
        self.history.append({'role': 'system', 'content': system_prompt})

    def add_user_response(self, response: str):
        self.history.append({'role': 'user', 'content': response})

    def add_assistant_response(self, response: str):
        self.history.append({'role': 'assistant', 'content': response})


class GPTVisionAgent(GPTAgent):
    def __init__(self, system_prompt: str, model: str = "gpt-4-vision-preview") -> None:
        super().__init__(system_prompt, model)

    def get_response(self, client: Client, image_path: str = "", text: str = ""):
        base64_image = encode_image(image_path)
        user_response = [
            {"type": "image_url",
             "image_url":
             {
                 "url": f"data:image/jpeg;base64,{base64_image}",
                 "detail": "low",
             },
             },
            {
                "type": "text",
                "text": text,
            }
        ]
        super.add_user_response(user_response)
        assistant_response = client.chat.completions.create(
            model=self.model,
            messages=self.history,
            max_tokens=300,
        )
        text_response = assistant_response.choices[0].message.content
        super.add_assistant_response(text_response)
        return text_response


class GPTTextAgent(GPTAgent):
    def __init__(self, system_prompt: str, model: str = "gpt-3.5-turbo") -> None:
        super().__init__(system_prompt, model)

    def get_response(self, client, text: str = ""):
        super.add_user_response(text)
        assistant_response = client.chat.completions.create(
            model=self.model,
            messages=self.history,
            max_tokens=300,
        )
        text_response = assistant_response.choices[0].message.content
        super.add_assistant_response(text_response)
        return text_response
