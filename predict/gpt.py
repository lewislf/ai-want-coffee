import cv2
import os
from api_key import OPENAI_API_KEY
import openai
from gpt4vision import request_description, set_pre_configuration, validate_task_img, validate_user_response, get_response
from time import sleep
from unidecode import unidecode
import numpy as np
import threading

########################################################################################################################
########################################################################################################################
# Substitua 'sua-chave-de-api-aqui' pela sua chave de API da OpenAI
openai.api_key = OPENAI_API_KEY

history = set_pre_configuration()
task = ""  # Declare the task variable globally
show_timer = False
timer_countdown = 5

ip_address = "rtsp://ip:port/h264_ulaw.sdp"
########################################################################################################################
########################################################################################################################

def analyze_frame(frame_count):
    image_path = f"path/to/your/capturas/passo_{frame_count}.jpg"
        
    response = request_description(task, image_path)
    print("response saiu")
    
    print("Response: " + str(response))

    if response is not None:
        print(response)
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
    base_path = "/path/to/yor/capturas/"

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
    if(show_timer):
        font_scale = 1
    else:
        font_scale = 0.5
    thickness = 1
    color = (255, 255, 255)  # Branco

    # Calcula a altura do texto para posicionar as linhas na imagem
    text_size = cv2.getTextSize('Tg', font, font_scale, thickness)[0]
    line_height = text_size[1] + 5  # Adiciona um pequeno espaço entre as linhas

    # Calcula a posição x e y para centralizar o texto na imagem
    text_height = len(lines) * line_height
    positional = 10
    text_width = max([cv2.getTextSize(line.strip(), font, font_scale, thickness)[0][0] for line in lines])
    if(show_timer):
        x = (width - text_width) // 2
        y = (height - text_height) - positional
    else:
        x = (width - text_width) // 2
        y = (height - text_height) - positional // 2

    for i, line in enumerate(lines):
        # Desenha cada linha do texto uma abaixo da outra
        text_y = y + i * line_height
        cv2.putText(frame, line.strip(), (x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)

ip_address = "rtsp://ip:port/h264_ulaw.sdp"
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

def main():
    global history, task, timer_countdown, show_timer  # Access the global task variable
    frame_count = 1

    while True:    
        task = get_response(history)        
        print("Tarefa atual: " + task)
        user_response = input("Você concluiu este passo? ").lower()
        
        user_response = validate_user_response(user_response, task)        
        history.append({'role': 'user', 'content': user_response})
        
        if user_response == "yes":
            history.append({'role': 'user', 'content': 'Passo concluído.'})
        elif user_response == "no":
            armazenaTask = task
            validacao = False
            while not validacao:
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
                    
                    if validacao == False:
                        task = 'Tarefa não concluída. Irei analisar mais uma vez.'
                        sleep(3)
                else:
                    print("Failed to capture a valid frame.")
        
                frame_count += 1
                
                # Lógica para processamento de imagem (não incluída aqui)
                print("Processamento de imagem necessário.")
            history.append({'role': 'user', 'content': 'Passo concluído.'})
        else:
            print("Entrada inválida. Por favor, digite novamente.")

if __name__ == "__main__":
    
    thread_show_image = threading.Thread(target=show_image)
    thread_show_image.start()
    main()
    thread_show_image.join()

    show_image()
