import cv2
import matplotlib.pyplot as plt
import IPython.display as display
from IPython.display import clear_output
import time
from mtcnn import MTCNN

def mtcnn_detector(video):
    detector = MTCNN()
    processing_times=[]
    capture_count = 0
    cap=cv2.VideoCapture(video)
    while cap.isOpened() and capture_count<11:
        ret, frame = cap.read()
        if not ret:
            break
        start_time = time.perf_counter()
        faces=detector.detect_faces(frame)
        for face in faces:
            x,y,w,h=face['box']
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),4)
            cv2.putText(frame,f"Confidence: {face['confidence']:.2f}",(x,y-10),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,0),2)
        end_time = time.perf_counter()
        processing_time = end_time - start_time
        if capture_count > 0:
            processing_times.append(processing_time)
        capture_count += 1
        cv2.putText(frame,f"Processing Time: {processing_time:.6f} seconds",(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,0),2)
        frame_rgb=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        clear_output(wait=True)
        # plt.clf()
        plt.imshow(frame_rgb)
        plt.title(f"processing time: {processing_time:.6f} seconds")
        plt.axis('off')
        # plt.pause(0.001)
        plt.savefig(f'mtcnn_{capture_count}.png')
        key=cv2.waitKey(1)
        if key & 0xFF==ord('q'):
            break
    if processing_times:
        average_processing_time=sum(processing_times)/len(processing_times)
        print(f"Average Processing Time(excluding first capture): {average_processing_time:.6f} seconds")
        plt.clf()
        plt.bar(range(len(processing_times)), processing_times, color='blue')
        plt.xlabel('Frame')
        plt.ylabel('Time(s)')
        plt.title('Time to detect face in frame')
        plt.savefig('mtcnn_bar.png')
    cap.release()
    return average_processing_time