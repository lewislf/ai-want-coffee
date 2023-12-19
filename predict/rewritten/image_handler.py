import cv2
import numpy as np
import os
import base64


class ImageHandler():
    cap: cv2.VideoCapture
    frame_count: int = 0
    
    def __init__(self, ip_address: str) -> None:
        self.cap = cv2.VideoCapture(ip_address)
        self.clear_captured_images_directory()

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
    
    def show_webcam(self) -> None:
        ret, frame = self.cap.read()
        if ret:
            cv2.imshow('Webcam', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return False
        return True
    
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
