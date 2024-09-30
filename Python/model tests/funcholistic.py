import cv2
import matplotlib.pyplot as plt
import IPython.display as display
from IPython.display import clear_output
import mediapipe as mp
import time

# cap=cv2.VideoCapture(0)
mp_holistics=mp.solutions.holistic
mp_drawings=mp.solutions.drawing_utils
holistic=mp_holistics.Holistic(min_detection_confidence=0.5,min_tracking_confidence=0.5)

def holistic_detector(video):
    with mp_holistics.Holistic(min_detection_confidence=0.5,min_tracking_confidence=0.5) as holistic:
        processing_times=[]
        capture_count=0
        cap=cv2.VideoCapture(video)
        while cap.isOpened() and capture_count<11:
            ret,frame=cap.read()
            if not ret:
                break
            start_time=time.perf_counter()
            image_rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            results=holistic.process(image_rgb)
            image_bgr=cv2.cvtColor(image_rgb,cv2.COLOR_RGB2BGR)

            if results.face_landmarks:
                h, w, _ = frame.shape
                face_landmarks = results.face_landmarks.landmark
                x_min = min([lm.x for lm in face_landmarks]) * w
                x_max = max([lm.x for lm in face_landmarks]) * w
                y_min = min([lm.y for lm in face_landmarks]) * h
                y_max = max([lm.y for lm in face_landmarks]) * h
                cv2.rectangle(image_bgr, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)

            end_time=time.perf_counter()
            processing_time=end_time-start_time
            if capture_count>0:
                processing_times.append(processing_time)
            capture_count+=1
            image_rgbnew=cv2.cvtColor(image_bgr,cv2.COLOR_BGR2RGB)
            clear_output(wait=True)
            plt.imshow(image_rgbnew)
            plt.axis('off')
            plt.title(f"Processing Time: {processing_time:.6f} seconds")
            # plt.show()
            plt.savefig(f'holistic_{capture_count}.png')
            print(f"Processing Time: {processing_time:.6f} seconds")
    if processing_times:
        average_processing_time=sum(processing_times)/len(processing_times)
        print(f"Average Processing Time(excluding first capture): {average_processing_time:.6f} seconds")
        plt.clf()
        plt.bar(range(len(processing_times)), processing_times, color='blue')
        plt.xlabel('Frame')
        plt.ylabel('Time(s)')
        plt.title('Time to detect face in frame')
        plt.savefig('holistic_bar.png')
    cap.release()
    return average_processing_time
    
