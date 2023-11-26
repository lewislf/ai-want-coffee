import openai
import requests
import json
import base64
from api_key import OPENAI_API_KEY

def set_pre_configuration(prompt=None):
    openai.api_key = OPENAI_API_KEY

    if prompt is None:
        prompt = [
            {'role': 'system', 'content': "Você se chama Clio e é uma Inteligência Computacional Autônoma (ICA) "
                                          "do laboratório de Computação de Alto Desempenho (LCAD) da Universidade "
                                          "Federal do Espírito Santo (UFES). Você é uma barista muito prestativa e é responsável por instruir o processo de fazer café coado da forma"
                                          "mais detalhada possível e em qualquer configuração de cozinha residencial em que esteja. Deverá me guiar "
                                          "fornecendo instruções sequenciais para o preparo do café, considere que será usado café em pó,"
                                          "e não será usado nada elétrico além do fogão. Você deve ser capaz de guiar um usuário que nunca preparou café antes,"
                                          "sempre pergunte se o usuário tem o item necessário para a tarefa e se o item é próprio para a tarefa,"
                                          "só prossiga com a tarefa se o usuário confirmar que tem o item."                                    
                                          "Suas instruções serão claras e diretas, não mais do que uma tarefa por vez e limite de 100 caracteres por tarefa. "
                                          "Exemplos de interações:" 
                                          "(EXEMPLO)'user': 'Clio, me pergunte se podemos iniciar'; 'system': 'Podemos iniciar o preparo do café?'; 'user': 'Sim';"
                                          "(EXEMPLO)'system': 'Verifique se você tem um recipiente para ferver a água"
                                          "(EXEMPLO)'user': 'Passo concluído.'; 'system': 'Encontre uma torneira'"
                                          "(EXEMPLO)'user': 'Passo concluído.'; 'system': 'Coloque água no recipiente'"
                                          "(EXEMPLO)'user': 'Passo concluído.'; 'system': 'Encontre um fogão'"
                                          "(EXEMPLO)'user': 'Passo concluído.'; 'system': 'Coloque o recipiente com a água no fogão'"},
            {'role': 'user', 'content': "Eu irei fazer uma demo testando através de imagens na tela do meu computador, considere-as como" 
             "'reais' para fins de teste. Me pergunte se podemos iniciar"},
        ]
        
    print("Configurando o modelo...")

    return prompt

# Function to encode the image
def encode_image(image_path:str):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def request_description(task:str, img_path:str, detail:str = "high"):
    prompt_image = f"Por favor, descreva os objetos na imagem relacionados à tarefa {task}, seja descritivo:"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
        {
            "role": "user", 
            "content": [
            {
                "type": "text",
                "text": prompt_image
            }
            ]
        }
        ],
        "max_tokens": 150
    }
    img = encode_image(img_path)
    img_info = {
            "type": "image_url",
            "image_url": {
            "url": f"data:image/jpeg;base64,{img}" ,
            "detail": detail
            }
        }
    payload['messages'][0]['content'].append(img_info)

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    if response.status_code != 200:
        print("'error': 'Failed to process the image.'")
        return
    response_content = response.content.decode('utf-8')
    description = json.loads(response_content)['choices'][0]['message']['content']
    return description

def get_response(history):
    openai.api_key = OPENAI_API_KEY
    
    if isinstance(history, str):
        history = json.loads(history)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = history,  # Use a lista completa de mensagens
        max_tokens=150
    )
    
    answer = response['choices'][0]['message']['content']

    # Atualize o history com a resposta da API
    history.append({'role': 'system', 'content': answer})

    return answer

def validate_task_img(description:str, task:str):
    openai.api_key = OPENAI_API_KEY
    prompt = f"""Analize task and description, if in the description has what the task want, say "yes", otherwise say "no": 
    Task: {task}
    Description: {description}
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
    response = response['choices'][0]['message']['content']
    if response.lower() == "yes":
        return True
    elif response.lower() == "no":
        return False
    else:
        print(f"VALIDATION ERROR: {response}")
        
def validate_user_response(user_response:str, task:str):
    openai.api_key = OPENAI_API_KEY
    prompt = f"""Analyze the task and user response. If the user response indicates a positive affirmation of the task, summarize the response as 'yes'. 
    If the user response indicates a desire to capture an image, summarize the response as 'capture'.
    Otherwise, summarize the response as 'no'.
    Task: {task}
    User response: {user_response}
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
    response = response['choices'][0]['message']['content']    
    response = response.lower()   
    
    if response == "yes":
        return "yes"
    elif response == "no":
        return "no"
    elif response == "capture":
        return "capture"
    else:
        print(f"VALIDATION ERROR: {response}")
