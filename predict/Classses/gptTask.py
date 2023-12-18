from config import PROMPT_INI,FIRST_ANSWER, MODE
from utils import encode_image, ask_gpt


class TaskManager:
    def __init__(self):
        self.conversa = PROMPT_INI
        self.task_atual = ""
        self.contador = 0
        
    def task_concluida(self, resposta):
        prompt = {
        "model": "gpt-4-1106-preview",
        "messages": [
            {
                'role': 'system', 
                'content': (
                    "Com base na resposta do usuário, diga 'yes' se a tarefa descrita foi concluida e 'no' se não foi concluida"
                    f"Task: {self.task_atual}"
                    f"Resposta do usuario: {resposta}"
                )
            },
        ],
        "max_tokens": 150
    }
        conclusao = ask_gpt(prompt)
        print(conclusao)
        return conclusao
        
    def get_task(self,response, img_path):
        if MODE == "NEGATIVE":
            if self.task_concluida(response):
                resposta = {
                    'role': 'user', 
                    'content': [(f"{response}")]
                    }
                self.contador +=1
                self.conversa["messages"].append(resposta)
            else:
                print("Image added")
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
                    
        elif MODE == "ALL":
            print("Image added2")
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

        self.task_atual = ask_gpt(self.conversa)
    
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

        self.task_atual = ask_gpt(self.conversa)
    
        task = {
                    'role': 'system', 
                    'content': (f"{self.task_atual}")
                    }
        self.contador +=1
        self.conversa["messages"].append(task)
    
    def printa_task(self):
        print(f"Task atual: {self.task_atual}")