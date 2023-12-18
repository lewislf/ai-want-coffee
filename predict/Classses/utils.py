import base64
import openai
import requests
import json
import os

from api_key import OPENAI_API_KEY

def encode_image(image_path:str):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
        
def ask_gpt(payload):
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    if response.status_code != 200:
        print("'error': 'Failed to process the image.'")
        return
    response_content = response.content.decode('utf-8')
    description = json.loads(response_content)['choices'][0]['message']['content']
    return description

def clear_captured_images_directory():
    directory = os.path.join(os.path.dirname(__file__), '..', 'CapturedImages')
    if os.path.exists(directory):
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
                
                