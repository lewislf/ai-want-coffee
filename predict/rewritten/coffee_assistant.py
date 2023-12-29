from openai import OpenAI
from threading import Thread, Event
from queue import Queue
import argparse
from agent import GPTVisionAgent
from image_handler import ImageHandler
from time import sleep

system_prompt = (
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

def show_webcam():
    camera_handler = ImageHandler(ip_address)
    while not end_program.is_set():
        if capture_frame_event.is_set():
            capture_frame_event.clear()
            queue_img.put(camera_handler.capture_webcam_frame())
            frame_captured_event.set()
        if has_new_text.is_set():
            has_new_text.clear()
            new_task = queue_text.get()
            camera_handler.update_task(new_task)
        if camera_handler.encerrado:
            end_program.set()
        camera_handler.show_webcam()
        
        

def main():
    client = OpenAI(api_key="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")
    coffee_assistant = GPTVisionAgent(system_prompt=system_prompt,
                                      model="gpt-4-vision-preview",
                                      image_history_rule='none')
    while not end_program.is_set():
        user_response = input("User: ")
        
        if not end_program.is_set():
            for i in range(3):
                text = f"Capturing frame in {3 - i}..."
                print(text)
                has_new_text.set()
                queue_text.put(text)
                sleep(0.75)
          
        if not end_program.is_set():
            capture_frame_event.set()
            frame_captured_event.wait()
            has_new_text.set()
            queue_text.put("Frame salvo! esperando resposta... ")
            
        if not end_program.is_set():
            image = queue_img.get()
            task = coffee_assistant.get_response(client, image, user_response)
            has_new_text.set()
            queue_text.put(task)
            print("Assistant: " + task)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="A program that does something.")
    parser.add_argument('ip_address', type=str,
                        help='The camera IP address to use')
    args = parser.parse_args()
    ip_address = args.ip_address

    capture_frame_event = Event()
    frame_captured_event = Event()
    has_new_text = Event()
    end_program = Event()
    queue_img = Queue()
    queue_text = Queue()

    thread_show_webcam = Thread(target=show_webcam)
    thread_show_webcam.start()

    main()

