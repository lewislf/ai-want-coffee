import cv2
import numpy as np
import os
import base64


class ImageHandler():
    cap: cv2.VideoCapture
    
    def __init__(self, ip_address: str) -> None:
        self.cap = cv2.VideoCapture(ip_address)
    
    def show_webcam(self) -> None:
        while True:
            ret, frame = self.cap.read()
            if ret:
                cv2.imshow('Webcam', frame)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
        self.cap.release()
        cv2.destroyAllWindows()

    def capture_webcam_frame(self, frame_count):
        # Capture a frame from the webcam
        ret, frame = self.cap.read()

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
        
        # Return the captured frame
        return self.encode_image(filename)
    
    def encode_image(self, image_path: str):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
