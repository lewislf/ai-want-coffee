# Import standard libraries
import json
import base64
import logging
from pathlib import Path
from typing import Union, Optional

# Import third-party libraries
import requests
import openai
from api_key import OPENAI_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)


class OpenAIManagement:
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = self.api_key
        
    
    def set_pre_configuration(prompt=None):
        openai.api_key = OPENAI_API_KEY

        if prompt is None:
            prompt = [
                {
                    'role': 'system', 
                    'content': (
                        "Você se chama Clio e é uma Inteligência Computacional Autônoma (ICA) "
                        "do laboratório de Computação de Alto Desempenho (LCAD) da Universidade "
                        "Federal do Espírito Santo (UFES). Você é uma barista muito prestativa e é responsável por instruir o processo de fazer café coado da forma"
                        "mais detalhada possível e em qualquer configuração de cozinha residencial em que esteja. Deverá me guiar "
                        "fornecendo instruções sequenciais para o preparo do café, considere que será usado café em pó,"
                        "Você deve ser capaz de guiar um usuário que nunca preparou café antes,"
                        "sempre pergunte se o usuário tem o item necessário para a tarefa e se o item é próprio para a tarefa,"
                        "só prossiga com a tarefa se o usuário confirmar que tem o item."                                    
                        "Suas instruções serão claras e diretas, não mais do que uma tarefa por vez e limite de 100 caracteres por tarefa. "
                        "Exemplos de interações:" 
                        "(EXEMPLO)'user': 'Clio, me pergunte se podemos iniciar'; 'system': 'Podemos iniciar o preparo do café?'; 'user': 'Step completed';"
                        "(EXEMPLO)'system': 'Verifique se você tem um recipiente para ferver a água"
                        "(EXEMPLO)'user': 'Step completed.'; 'system': 'Encontre uma torneira'"
                        "(EXEMPLO)'user': 'Step completed.'; 'system': 'Coloque água no recipiente'"
            
                    "Clio, me pergunte se podemos iniciar o preparo do café?": "Podemos iniciar o preparo do café?")
                }
            ]
            
        print("Configurando o modelo...")

        return prompt


    def _create_headers(self) -> dict:
        """
        Creates headers for the API request.

        :return: Dictionary containing headers.
        """
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    
    def get_response(self, history):
        """
        Gets a response from the OpenAI API based on the provided history.

        :param history: The conversation history to base the response on.
        :return: The response from the API as a string.
        """
        # Ensure that history is a list of dictionaries.
        if isinstance(history, str):
            history = json.loads(history)

        # Construct the payload for the API call.
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": history,  # This should be a list of message dictionaries.
        }

        try:
            # Make the API call.
            response = openai.ChatCompletion.create(**payload)
            # Extract the content from the response.
            answer = response.choices[0].message['content']
        except Exception as e:
            # Handle exceptions and perhaps log them.
            print(f"An error occurred: {e}")
            answer = ""

        return answer


class VisionAssistant(OpenAIManagement):
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.openai = openai

    
    def _create_payload(self, prompt_image: str, detail: str, img_path: str) -> dict:
        """
        Creates the payload for the API request.

        :param prompt_image: The image prompt.
        :param detail: Level of detail for the description.
        :param img_path: Path to the image file.
        :return: Payload for the API request.
        """
        img = self._encode_image_to_base64(img_path)
        img_info = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{img}",
                "detail": detail
            }
        }
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": prompt_image}]}
            ],
            "max_tokens": 150
        }
        payload['messages'][0]['content'].append(img_info)
        return payload
    
    
    def _encode_image_to_base64(self, image_path: Union[str, Path]) -> str:
        """
        Encodes an image file to base64.

        :param image_path: Path to the image file.
        :return: Base64 encoded string.
        """
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string
    
    
    def request_description(self, task: str, img_path: str, detail: str = "high") -> Optional[str]:
        """
        Requests a description of the image related to a specific task.

        :param task: The task to describe.
        :param img_path: Path to the image file.
        :param detail: Level of detail for the description.
        :return: Description string or None if there was an error.
        """
        prompt_image = f"Por favor, descreva os objetos na imagem relacionados à tarefa {task}, seja descritivo:"
        headers = self._create_headers()
        payload = self._create_payload(prompt_image, detail, img_path)

        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Failed to process the image: {e}")
            return None

        description = response.json()['choices'][0]['message']['content']
        return description
    
    
    def validate_if_capture_or_substitute(self, user_response: str, task: str) -> list:
        """
        Determines the user's intention based on their response and the provided task.

        :param user_response: The user's response.
        :param task: The task to be validated against the user's response.
        :return: A list containing the intention and the user's response.
        """
        openai.api_key = OPENAI_API_KEY
        prompt = f"""
        Based on the user's response and the provided task, determine the user's intention.
        If the user's response suggests the desire to capture an image, classify the response as 'capture'.
        If the user's response suggests the desire to substitute the current task with another, classify the response as 'substitute'.
        If the user's intention is unclear, classify it as 'unclear'.
        Task: {task}
        User's response: {user_response}
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=150
        )
        response_text = response['choices'][0]['message']['content'].lower()

        if "capture" in response_text:
            return ["capture", user_response]
        elif "substitute" in response_text:
            return ["substitute", user_response]
        else:
            return ["unclear", user_response]
    
    
    def get_equivalent_task(self, task: str, description: str) -> str:
        """
        Gets an equivalent task from the OpenAI.

        :param task: The task to be validated against the description.
        :return: The equivalent task.
        """
        prompt = f"""Analize task and description, if in the description has what the task want, say "yes", otherwise say "no": 
        Task: {task}
        Description: {description}
        """

        try:
            response = self.openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "GPT4Vision", "content": prompt}],
                max_tokens=150
            )
        except self.openai.error.OpenAIError as e:
            logging.error(f"Error in validation: {e}")
            return False

        response_text = response['choices'][0]['message']['content'].lower()
        return "yes" in response_text
    
    
    def validate_task_img(self, description: str, task: str) -> bool:
        """
        Validates if the image description matches the task requirements.

        :param description: The description of the image.
        :param task: The task to be validated against the description.
        :return: True if the task is validated, False otherwise.
        """
        prompt = f"""Analize task and description, if in the description has what the task want, say "yes", otherwise say "no": 
        Task: {task}
        Description: {description}
        """

        try:
            response = self.openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": prompt}],
                max_tokens=150
            )
        except self.openai.error.OpenAIError as e:
            logging.error(f"Error in validation: {e}")
            return False

        response_text = response['choices'][0]['message']['content'].lower()
        return "yes" in response_text


class RobotAIManager (OpenAIManagement):
    
    def generate_robot_action_plan(self, task: str, robot_actions_log: str) -> str:
        """
        Generates a step-by-step action plan for the robot to perform based on the given task.

        :param task: The task to be performed.
        :param robot_actions_log: The log of previous robot actions.
        :return: The updated robot_actions_log string.
        """
        prompt = f"""Analyze the task and provide a step-by-step action plan for the robot to perform:
        Consider the context of the history and the given task.
        Provide actions like: 'Look right', 'Look left', 'Walk', 'Take', 'Grab', 'Put', 'Open', 'Close', 'Turn on', 'Turn off', 'Turn up', 'Turn down', 
        'Turn around', 'Turn left', 'Turn right', 'Turn back', 'Turn front'.
        Look at the robot_actions_log to see the previous actions and know what the robot has already done.
        Task: {task}
        History: {robot_actions_log}
        """

        try:
            response = self.openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "RobotAIManager", "content": prompt}],
                max_tokens=150
            )
        except self.openai.error.OpenAIError as e:
            logging.error(f"Error in generating action plan: {e}")
            return robot_actions_log

        response_text = response['choices'][0]['message']['content'].lower()
        robot_actions_log += response_text + "\n"
        return robot_actions_log
    
    
    def default(self, o):
        if isinstance(o, OpenAIManagement):
            return o.__dict__
        return super().default(o)


