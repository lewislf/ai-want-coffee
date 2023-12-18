from typing import List
from openai import Client


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
    image_history_rule: str
    def __init__(self, system_prompt: str, model: str = "gpt-4-vision-preview", image_history_rule: str = "all") -> None:
        super().__init__(system_prompt, model)
        assert image_history_rule in ['all', 'none']
        self.image_history_rule = image_history_rule


    def get_response(self, client: Client, image, text: str = ""):
        user_response = [
            {"type": "image_url",
             "image_url":
             {
                 "url": f"data:image/jpeg;base64,{image}",
                 "detail": "low",
             },
             },
            {
                "type": "text",
                "text": text,
            }
        ]
        self.add_user_response(user_response)
        assistant_response = client.chat.completions.create(
            model=self.model,
            messages=self.history,
            max_tokens=300,
        )
        self.image_history_handler(text)

        text_response = assistant_response.choices[0].message.content
        self.add_assistant_response(text_response)
        return text_response
    
    def image_history_handler(self, text):
        if self.image_history_rule == 'none':
            self.history.pop()
            self.add_user_response(text)


class GPTTextAgent(GPTAgent):
    def __init__(self, system_prompt: str, model: str = "gpt-3.5-turbo") -> None:
        super().__init__(system_prompt, model)

    def get_response(self, client, text: str = ""):
        self.add_user_response(text)
        assistant_response = client.chat.completions.create(
            model=self.model,
            messages=self.history,
            max_tokens=300,
        )
        text_response = assistant_response.choices[0].message.content
        self.add_assistant_response(text_response)
        return text_response
