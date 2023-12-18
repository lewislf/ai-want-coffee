import cv2
import os
import numpy as np
import threading
from time import sleep
from unidecode import unidecode
from api_key import OPENAI_API_KEY
from api_key import LOCAL_CAMERA
import openai
from gpt4vision import *

print(LOCAL_CAMERA)

########################################################################################################################
########################################################################################################################
# Variáveis globais
openai.api_key = OPENAI_API_KEY
history = set_pre_configuration()
task = ""  # Declare the task variable globally
show_timer = False
timer_countdown = 5
ip_address = LOCAL_CAMERA # Substitua ip e porta pelo IP e porta da sua webcam
########################################################################################################################
########################################################################################################################

def analyze_frame(frame_count):
    script_dir = os.path.dirname(__file__)
    image_path = os.path.join(script_dir, '..', f'CapturedImages/passo_{frame_count}.jpg') 

    response = request_description(task, image_path)
    if response is not None:
        print("\nResponse: " + str(response))
    else:
        print("Error in API request: None")
        response = "Analysis failed"
    return response

def capture_webcam_frame(frame_count) -> np.ndarray:
    """
    Connects to the webcam IP, captures a unique frame, and returns the captured frame.
    :param ip_address: IP address of the webcam.
    :param task_name: Name of the current task to use in the filename.
    :param frame_count: Frame count to ensure unique filenames.
    :return: Captured frame as a numpy array.
    """
    local_cap = cv2.VideoCapture(ip_address)

    # Check if the connection was successful
    if not local_cap.isOpened():
        print("Failed to connect to webcam.")
        return None

    # Capture a frame from the webcam
    ret, frame = local_cap.read()

    # Check if the frame was captured successfully
    if not ret:
        print("Failed to capture frame.")
        local_cap.release()
        return None

    # Define the path to the folder where the captured frames will be saved
    script_dir = os.path.dirname(__file__)  
    base_path = os.path.join(script_dir, '..', 'CapturedImages') 

    # Create the folder if it doesn't exist
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    # Define the path to the file where the captured frame will be saved
    filename = os.path.join(base_path, f"passo_{frame_count}.jpg")

    # Save the captured frame to the file
    cv2.imwrite(filename, frame)

    # Print the path to the saved file
    print(f"Frame saved to: {filename}")
    
    local_cap.release()

    # Return the captured frame
    return frame

def draw_text(text, height, width, frame):
    # Convert special characters to ASCII
    text = unidecode(text)

    # Quebra o texto em uma lista de linhas com no máximo 30 caracteres
    words = text.split(' ')
    lines = []
    current_line = ''
    for word in words:
        if len(current_line + ' ' + word) <= 30:
            current_line += ' ' + word
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)

    # Define as variáveis para o texto
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1 if show_timer else 0.5
    thickness = 1
    color = (255, 255, 255)  # Branco

    # Calcula a altura do texto para posicionar as linhas na imagem
    text_size = cv2.getTextSize('Tg', font, font_scale, thickness)[0]
    line_height = text_size[1] + 5  # Adiciona um pequeno espaço entre as linhas

    # Calcula a posição x e y para centralizar o texto na imagem
    text_height = len(lines) * line_height
    positional = 10
    text_width = max([cv2.getTextSize(line.strip(), font, font_scale, thickness)[0][0] for line in lines])
    
    x = (width - text_width) // 2
    y = (height - text_height) - positional if show_timer else (height - text_height) - positional // 2

    for i, line in enumerate(lines):
        # Desenha cada linha do texto uma abaixo da outra
        text_y = y + i * line_height
        cv2.putText(frame, line.strip(), (x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)

cap = cv2.VideoCapture(ip_address)  # O argumento 0 indica a primeira webcam disponível

def show_image():
    global cap

    # Verifica se a webcam foi aberta corretamente
    if not cap.isOpened():
        print("Erro ao abrir a webcam.")
        exit()

    # Loop de captura de vídeo
    while True:
        # Lê o próximo quadro da webcam
        ret, frame = cap.read()

        # Verifica se o quadro foi lido corretamente
        if not ret:
            print("Erro ao ler o quadro.")
            break

        # Obter as dimensões da imagem
        height, width = frame.shape[:2]

        if show_timer:
            draw_text(str(timer_countdown), height, width, frame)
        else:
            draw_text(task, height, width, frame)

        # Exibe o quadro em uma janela
        cv2.imshow('Webcam com Texto', frame)

        # Verifica se a tecla 'q' foi pressionada para encerrar o loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Libera os recursos quando o loop é encerrado
    cap.release()
    cv2.destroyAllWindows()

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

def main():
    clear_captured_images_directory()
    global history, task, timer_countdown, show_timer  # Access the global task variable
    frame_count = 1
    trying_new_task = False

    while True:
        if not trying_new_task:
            task = get_response(history) 
            print("\nTarefa atual: " + task)
        trying_new_task = False

        user_response = input("Você concluiu este passo? ").lower()
        user_response = validate_user_response(user_response, task)  

        if user_response:      
            # print("Histórico: " +  user_response[1]) # Debug
            history.append({'role': 'user', 'content': user_response[1]})
            
            if "yes" in user_response[0]:
                history.append({'role': 'user', 'content': 'Passo concluído.'})
            elif "no" in user_response[0]:
                armazenaTask = task
                validacao = False
                # print("Histórico: " + str(history)) # Debug
            
                while not validacao:
                    # Pergunta se o usuário deseja capturar outra imagem ou tentar uma tarefa substituta
                    user_response = input("\nTarefa não concluída.\nDeseja capturar uma imagem ou tentar uma tarefa substituta? ").lower()
                    user_intent = validate_if_capture_or_substitute(user_response, task)
                    
                    # Enquanto a resposta do usuario nao for clara, o loop continua
                    while "unclear" in user_intent[0]:
                        user_response = input("Resposta não compreendida. Por favor, esclareça sua resposta.\nDeseja capturar outra imagem ou tentar uma tarefa substituta? ").lower()
                        user_intent = validate_if_capture_or_substitute(user_response, task)

                    # print("user_response[0] == " + str(user_response[0])) # Debug

                    if "capture" in user_intent[0]:
                        task = 'Inicializando a captura de imagem...'
                        sleep(3)
                        print("Iniciando captura de imagem...")
                        show_timer = True
                        for i in range(3):
                            timer_countdown = 3 - i
                            sleep(0.75)

                        task = 'Analisando a imagem...'
                        show_timer = False
                        task = armazenaTask
                        
                        frame = capture_webcam_frame(frame_count)             
                        
                        if frame is not None:    
                            description = analyze_frame(frame_count)
                            validacao = validate_task_img(description, task)
                        else:
                            print("Failed to capture a valid frame.")
                
                        frame_count += 1
                 
                    # Se o usuário deseja tentar uma tarefa substituta, o loop é reiniciado com a nova tarefa
                    elif"substitute" in user_intent[0]:
                        new_task = get_equivalent_task(task) 
                        task = new_task
                        print("\n\nNova tarefa: " + task)
                        trying_new_task = True
                        break 
                    else:
                        print("Erro na validação da resposta do usuário.")
                
                history.append({'role': 'user', 'content': 'Passo concluído.'})
            else:
                print("Entrada inválida. Por favor, digite novamente.")
        else:
            print("Erro na validação da resposta do usuário. Por favor, tente novamente.")
            
        # print("Histórico: " + str(history)) # Debug

if __name__ == "__main__":
    thread_show_image = threading.Thread(target=show_image)
    thread_show_image.start()
    main()
    thread_show_image.join()
    show_image()
