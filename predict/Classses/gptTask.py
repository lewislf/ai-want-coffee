import openai

from config import PROMPT_INI,FIRST_ANSWER
from api_key import OPENAI_API_KEY
from utils import encode_image, ask_gpt_3_5, ask_gpt_vision


class TaskManager:
    def __init__(self):
        self.conversa = PROMPT_INI
        self.task_atual = ""
        self.contador = 0
        
    def isYes(self,text):
        texto = f"""Analyze the task and user response. If the user response indicates a positive affirmation summarize the response as 'yes'. If not, summarize the response as 'no'.
        User response: {text}
        """

        return ask_gpt_3_5(texto)
        
    def get_task(self,response, img_path):
    
        resposta = {
                'role': 'user', 
                'content': [(f"{response}, segue imagem do meu local: ")]
                }
        self.contador +=1
        self.conversa["messages"].append(resposta)
        
        img = encode_image(img_path)
        img_info = {
        "type": "image_url",
        "image_url": {
        "url": f"data:image/jpeg;base64,{img}" ,
        "detail": "low"
        }
        }
        self.conversa["messages"][self.contador]["content"].append(img_info)

        self.task_atual = ask_gpt_vision(self.conversa)
    
        task = {
                    'role': 'system', 
                    'content': (f"{self.task_atual}")
                    }
        self.contador +=1
        self.conversa["messages"].append(task)
        
    def get_first_task(self):
        resposta = {
                'role': 'user', 
                'content': [(f"{FIRST_ANSWER}")]
                }
        self.contador +=1
        self.conversa["messages"].append(resposta)

        self.task_atual = ask_gpt_vision(self.conversa)
    
        task = {
                    'role': 'system', 
                    'content': (f"{self.task_atual}")
                    }
        self.contador +=1
        self.conversa["messages"].append(task)
    
    def printa_task(self):
        print(f"Task atual: {self.task_atual}")