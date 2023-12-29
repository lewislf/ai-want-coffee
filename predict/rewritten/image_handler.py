import cv2
import os
import base64
from unidecode import unidecode

class ImageHandler():
    cap: cv2.VideoCapture
    frame_count: int = 0
    
    def __init__(self, ip_address: str) -> None:
        self.cap = cv2.VideoCapture(ip_address)
        self.clear_captured_images_directory()
        self.text = "Quando quiser fazer cafe estou a sua disposicao."
        self.encerrado = False

    def clear_captured_images_directory(self):
        directory = os.path.join(os.path.dirname(__file__), '..', 'CapturedImages')
        if os.path.exists(directory):
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
    
    def draw_text(self,text:str, frame):
        text = unidecode(text)
        height, width = frame.shape[:2]

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
        font_scale = 0.5
        thickness = 1
        color = (255, 0, 0)

        text_size = cv2.getTextSize('Tg', font, font_scale, thickness)[0]
        line_height = text_size[1] + 5

        text_height = len(lines) * line_height
        positional = 10
        text_width = max([cv2.getTextSize(line.strip(), font, font_scale, thickness)[0][0] for line in lines])
        
        x = (width - text_width) // 2
        y = (height - text_height) - positional // 2

        for i, line in enumerate(lines):
            text_y = y + i * line_height
            cv2.putText(frame, line.strip(), (x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)
    
    def update_task(self,new_text:str):
        self.text = new_text
    
    def show_webcam(self) -> None:
        ret, frame = self.cap.read()
        if ret:
            self.draw_text(self.text,frame)
            cv2.imshow('Webcam', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.cap.release()
            cv2.destroyAllWindows()  
            self.encerrado = True
    
    def capture_webcam_frame(self):
        # Capture a frame from the webcam
        ret, frame = self.cap.read()

        # Define the path to the folder where the captured frames will be saved
        script_dir = os.path.dirname(__file__)  
        base_path = os.path.join(script_dir, '..', 'CapturedImages') 

        # Create the folder if it doesn't exist
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        # Define the path to the file where the captured frame will be saved
        filename = os.path.join(base_path, f"passo_{self.frame_count}.jpg")

        # Save the captured frame to the file
        cv2.imwrite(filename, frame)

        # Print the path to the saved file
        print(f"Frame saved to: {filename}")

        # Increment the frame count
        self.frame_count += 1

        # Return the captured frame
        return self.encode_image(filename)
    
    def encode_image(self, image_path: str):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
