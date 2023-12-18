from openai import OpenAI
import threading
import argparse
import cv2
from agent import GPTTextAgent
from image_handler import ImageHandler


system_prmpt = (
    "Você se chama Clio e é uma Inteligência Computacional Autônoma (ICA) "
    "do laboratório de Computação de Alto Desempenho (LCAD) da Universidade "
    "Federal do Espírito Santo (UFES).\n"
    "Você é uma barista muito prestativa e é responsável por instruir o processo de fazer café coado da forma "
    "mais detalhada possível e em qualquer configuração de cozinha residencial em que esteja. Deverá me guiar "
    "fornecendo instruções sequenciais para o preparo do café, considere que será usado café em pó.\n"
    "Você deve ser capaz de guiar um usuário que nunca preparou café antes,"
    "sempre pergunte se o usuário tem o item necessário para a tarefa e se o item é próprio para a tarefa, "
    "só prossiga com a tarefa se o usuário confirmar que tem o item.\n"                                    
    "Suas instruções serão claras e diretas, não mais do que uma tarefa por vez e limite de 100 caracteres por tarefa. "
    "Exemplos de interações:\n" 
    "(EXEMPLO)'user': 'Clio, me pergunte se podemos iniciar'; 'system': 'Podemos iniciar o preparo do café?'; 'user': 'Sim';\n"
    "(EXEMPLO)'system': 'Verifique se você tem um recipiente para ferver a água\n"
    "(EXEMPLO)'user': 'Passo concluído.'; 'system': 'Encontre uma torneira'\n"
    "(EXEMPLO)'user': 'Passo concluído.'; 'system': 'Coloque água no recipiente'\n"
)


def main(ip_address):
    global system_prompt
    client = OpenAI()
    coffee_agent = GPTTextAgent(system_prompt, "gpt-3.5-turbo")
    cap = cv2.VideoCapture(ip_address)
    img_handler = ImageHandler(cap)

    thread_show_webcam = threading.Thread(target=img_handler.show_webcam)
    thread_show_webcam.start()

    user_response = (
        "Eu irei fazer uma demo testando através de imagens na tela do meu computador, considere-as como" 
        "'reais' para fins de teste. Me pergunte se podemos iniciar"
    )
    
    while True:
        response = coffee_agent.get_response(client, user_response)
        

    thread_show_webcam.join()


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="A program that does something.")
    parser.add_argument('ip_address', type=str, help='The camera IP address to use')
    args = parser.parse_args()
    ip_address = args.ip_address
    main(ip_address)