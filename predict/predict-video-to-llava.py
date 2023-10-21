import os
import requests
from ultralytics import YOLO
import cv2

video_path = "E:\\Arquivos\\ai-want-coffee\\data\\sample_videos\\cozinha01.mp4"

file_name_without_extension = os.path.splitext(os.path.basename(video_path))[0]
output_dir = "E:\\Arquivos\\ai-want-coffee\\data\\results"

video_path_out = os.path.join(output_dir, f"{file_name_without_extension}.mp4")

cap = cv2.VideoCapture(video_path)

ret, frame = cap.read()    
H, W, _ = frame.shape
out = cv2.VideoWriter(video_path_out, cv2.VideoWriter_fourcc(*'MP4V'), int(cap.get(cv2.CAP_PROP_FPS)), (W, H))

model = YOLO('yolov8n.pt')

threshold = 0.5
object_of_interest = ["umbrella", "coffee filter", "coffee cup", "cup", "person"]

save_dir = "E:\\Arquivos\\ai-want-coffee\\data\\results\\object_of_interest"
os.makedirs(save_dir, exist_ok=True)

image_counter = 0

while ret:
    results = model(frame)[0]

    for result in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result

        if score > threshold:
            detected_object = results.names[int(class_id)].lower()

            if detected_object in object_of_interest:
                # Draw for image
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4)
                cv2.putText(frame, detected_object, (int(x1), int(y1 - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)
                
                image_filename = os.path.join(save_dir, f"image_{image_counter}.jpg")
                cv2.imwrite(image_filename, frame)
                image_counter += 1

                # Send the image to Llava for analysis
                url = "https://llava.hliu.cc/"  # Llava API endpoint !?!?!?
                files = {'image': open(image_filename, 'rb')}
                response = requests.post(url, files=files)
                print("Sent to Llava:", response.json())

            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4)
            cv2.putText(frame, detected_object, (int(x1), int(y1 - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)

    out.write(frame)
    ret, frame = cap.read()

cap.release()
out.release()
cv2.destroyAllWindows()
