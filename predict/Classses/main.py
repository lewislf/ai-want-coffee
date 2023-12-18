import threading
import cv2

from api_key import LOCAL_CAMERA
from video import VideoManager
from gptTask import TaskManager
from cronometro import Cronometro
from utils import clear_captured_images_directory

def main():
    video = VideoManager(LOCAL_CAMERA)
    gptTask = TaskManager()
    
    def show_image():
        while not video.encerrado:
            video.atualizar(gptTask.task_atual)
    thread_show_image = threading.Thread(target=show_image)
    thread_show_image.start()
    
    clear_captured_images_directory()
    gptTask.get_first_task()
    gptTask.printa_task()
    while not video.encerrado:
        resposta = input("Digite o resultado da task: ")
        print("oi")
        video.get_frame()
        print("ola")
        gptTask.get_task(resposta,video.path_to_image())
        gptTask.printa_task()

if __name__ == "__main__":

    main()      
