import cv2
import os
import numpy as np
import threading
from time import sleep
from unidecode import unidecode
from api_key import OPENAI_API_KEY, LOCAL_CAMERA
import openai
from gpt4vision import OpenAIManagement, VisionAssistant, RobotAIManager


# Classes
openai_manager = OpenAIManagement(api_key= OPENAI_API_KEY)
vision_assistant = VisionAssistant(api_key=OPENAI_API_KEY)
robot_manager = RobotAIManager(api_key=OPENAI_API_KEY)


# Global Variables
openai.api_key = OPENAI_API_KEY
history = []
history = OpenAIManagement.set_pre_configuration()
task = ""
show_timer = False
timer_countdown = 5
ip_address = LOCAL_CAMERA
cap = cv2.VideoCapture(ip_address)



def analyze_frame(frame_count):
    script_dir = os.path.dirname(__file__)
    image_path = os.path.join(script_dir, '..', f'CapturedImages/passo_{frame_count}.jpg') 

    response = vision_assistant.request_description(task, image_path)
    if response is not None:
        print("\nResponse: " + str(response))
    else:
        print("Error in API request: None")
        response = "Analysis failed"
    return response


def capture_webcam_frame(frame_count) -> np.ndarray:
    local_cap = cv2.VideoCapture(ip_address)

    if not local_cap.isOpened():
        print("Failed to connect to webcam.")
        return None

    ret, frame = local_cap.read()

    if not ret:
        print("Failed to capture frame.")
        local_cap.release()
        return None

    script_dir = os.path.dirname(__file__)  
    base_path = os.path.join(script_dir, '..', 'CapturedImages') 

    if not os.path.exists(base_path):
        os.makedirs(base_path)

    script_dir = os.path.join(base_path, f"passo_{frame_count}.jpg")
    
    cv2.imwrite(script_dir, frame) 
    
    print(f"Frame without matrix saved to: {script_dir}")
    
    local_cap.release()

    return frame


def draw_text(text, height, width, frame):
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
    font_scale = 1 if show_timer else 0.5
    thickness = 1
    color = (255, 255, 255)

    text_size = cv2.getTextSize('Tg', font, font_scale, thickness)[0]
    line_height = text_size[1] + 5

    text_height = len(lines) * line_height
    positional = 10
    text_width = max([cv2.getTextSize(line.strip(), font, font_scale, thickness)[0][0] for line in lines])
    
    x = (width - text_width) // 2
    y = (height - text_height) - positional if show_timer else (height - text_height) - positional // 2

    for i, line in enumerate(lines):
        text_y = y + i * line_height
        cv2.putText(frame, line.strip(), (x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)


def show_image():
    global cap

    if not cap.isOpened():
        print("Failed to open webcam.")
        exit()

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to read frame.")
            break

        height, width = frame.shape[:2]

        if show_timer:
            draw_text(str(timer_countdown), height, width, frame)
        else:
            draw_text(task, height, width, frame)

        cv2.imshow('Webcam com Texto', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def capture_and_analyze_frame(frame_count, task):
    global show_timer, timer_countdown

    task = 'Initializing image capture...'
    sleep(3)
    print("Initiating image capture...")
    show_timer = True

    for i in range(3):
        timer_countdown = 3 - i
        sleep(0.75)

    task = 'Analyzing image...'
    show_timer = False

    frame = capture_webcam_frame(frame_count)

    return frame


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
    #clear_captured_images_directory()

    global history, task, timer_countdown, show_timer
    frame_count = 1
    trying_new_task = False

    while True:
        if not trying_new_task:
            task = openai_manager.get_response(history)             
            print("\nCurrent Task: " + task)

        trying_new_task = False

        print("\n", history)
        frame = capture_and_analyze_frame(frame_count, task)
            
        if frame is not None:    
            description = analyze_frame(frame_count)
            vision_assistant.validate_task_img(description, task)
        else:
            print("Failed to capture a valid frame.")

        user_response = vision_assistant.validate_task_img(description, task) 

        if user_response:
            history.append({'role': 'OpenAIManagement', 'content': task})
            history.append({'role': 'user', 'content': 'Step completed.'})
        elif user_response is False:
            validacao = False
            analyze_validation = False  # Initialize analyze_validation variable

            while not validacao:
                user_intent = vision_assistant.validate_if_capture_or_substitute(description, task)
                
                while user_intent is False:
                    user_response = False
                    user_intent = vision_assistant.validate_if_capture_or_substitute(user_response, task)

                if user_intent:
                    frame = capture_and_analyze_frame(frame_count, task)
                    
                    if frame is not None:
                        description = analyze_frame(frame_count)
                        analyze_task_substitutive_or_capture = vision_assistant.validate_if_capture_or_substitute(description, task)
                        frame_count += 1

                    if analyze_task_substitutive_or_capture is True:
                        task = vision_assistant.get_equivalent_task(task, description) 
                        print("\n\nNew Task: " + task)
                        trying_new_task = True
                        analyze_validation = vision_assistant.validate_task_img(description, task)
                        break 
                    elif analyze_task_substitutive_or_capture is False:
                        capture_and_analyze_frame(frame_count, task)                        
                        description = analyze_frame(frame_count)
                        analyze_validation = vision_assistant.validate_task_img(description, task)
                        
                    if analyze_validation is True:
                        history.append({'role': 'OpenAIManagement', 'content': task})
                        history.append({'role': 'user', 'content': 'Step completed.'})
                        validacao = True                        
                        
                    else:
                        print("Error in validating user response.")
                    
                    history.append({'role': 'user', 'content': 'Step completed.'})
                else:
                    print("Invalid input. Please try again.")
        else:
            print("Error in validating user response. Please try again.")


if __name__ == "__main__":
    thread_show_image = threading.Thread(target=show_image)
    thread_show_image.start()
    main()
    thread_show_image.join()
    show_image()
