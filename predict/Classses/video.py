import cv2
from unidecode import unidecode
import os

from api_key import LOCAL_CAMERA
from cronometro import Cronometro

class VideoManager:
    def __init__(self, ip_address:str):
        self.cap = cv2.VideoCapture(ip_address)
        if not self.cap.isOpened():
            print("Failed to open webcam.")
            exit()
            
        self.cronometro = Cronometro()
        self.timer = False
        self.encerrado = False
        self.contador = 0
            
    def draw_text(self,text, height, width, frame):
        text = unidecode(text)

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

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1 if self.timer else 0.5
        thickness = 1
        color = (255, 255, 255)

        text_size = cv2.getTextSize('Tg', font, font_scale, thickness)[0]
        line_height = text_size[1] + 5

        text_height = len(lines) * line_height
        positional = 10
        text_width = max([cv2.getTextSize(line.strip(), font, font_scale, thickness)[0][0] for line in lines])
        
        x = (width - text_width) // 2
        y = (height - text_height) - positional if self.timer else (height - text_height) - positional // 2

        for i, line in enumerate(lines):
            text_y = y + i * line_height
            cv2.putText(frame, line.strip(), (x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)
            
    def iniciar_timer(self):
        self.timer = True
        self.cronometro.reset()
        
    def base_path(self):
        script_dir = os.path.dirname(__file__)  
        base_path = os.path.join(script_dir, '..', 'CapturedImages') 
        return base_path
        
    def path_to_image(self):
        base_path = self.base_path()
        filename = os.path.join(base_path, f"passo_{self.contador}.jpg")
        return filename
        
    def get_frame(self):
        """
        Connects to the webcam IP, captures a unique frame, and returns the captured frame.
        :param ip_address: IP address of the webcam.
        :param task_name: Name of the current task to use in the filename.
        :param frame_count: Frame count to ensure unique filenames.
        :return: Captured frame as a numpy array.
        """
        local_cap = cv2.VideoCapture(LOCAL_CAMERA)
        
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
        base_path = self.base_path()

        # Create the folder if it doesn't exist
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        # Define the path to the file where the captured frame will be saved
        self.contador += 1
        filename = self.path_to_image()

        # Save the captured frame to the file
        cv2.imwrite(filename, frame)

        # Print the path to the saved file
        print(f"Frame saved to: {filename}")
            
    def atualizar(self, task):
        ret, frame = self.cap.read()

        if not ret:
            print("Failed to read frame.") 
            self.cap.release()
            cv2.destroyAllWindows()  
            self.encerrado = True
            
        height, width = frame.shape[:2]
        
        if self.cronometro.tempo_passado() > 3:
            self.cronometro.reset()
            self.timer = False
        
        if self.timer:
            self.draw_text(str(3-self.cronometro.tempo_passado()//1), height, width, frame)
        else:
            self.draw_text(task, height, width, frame)

        cv2.imshow('Webcam com Texto', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.cap.release()
            cv2.destroyAllWindows()
            self.encerrado = True
            
            
