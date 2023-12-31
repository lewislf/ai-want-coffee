import base64
import cv2
import os
import numpy as np


# Function to encode the image
def encode_image(image_path:str):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def capture_webcam_frame(frame_count, ip_address) -> np.ndarray:
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