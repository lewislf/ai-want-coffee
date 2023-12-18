import cv2


class ImageHandler():
    cap: cv2.VideoCapture
    
    def __init__(self, cap: cv2.VideoCapture) -> None:
        self.cap = cap
    
    def show_webcam(self):
        while True:
            ret, frame = self.cap.read()
            if ret:
                cv2.imshow('Webcam', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.cap.release()
        cv2.destroyAllWindows()
