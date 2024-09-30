import cv2
import matplotlib.pyplot as plt
import IPython.display as display
from IPython.display import clear_output
import time

def haar_detector(video):
    cap=cv2.VideoCapture(video)
    face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    processing_times = []
    capture_count = 0
    while cap.isOpened() and capture_count<11:
        ret, frame = cap.read()
        if not ret:
            break
        start_time = time.perf_counter()
        gray_image = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray_image,scaleFactor=1.05,minNeighbors=7,minSize=(40,40))
        for (x,y,w,h) in faces:
            cv2.rectangle(frame,(x,y),(x+h,y+w),(0,255,0),4)
        end_time=time.perf_counter()
        processing_time=end_time-start_time
        if capture_count > 0:
            processing_times.append(processing_time)
        capture_count += 1
        image_rgb=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        clear_output(wait=True)
        plt.imshow(image_rgb)
        plt.axis('off')
        plt.title(f"Processing Time: {processing_time:.6f} seconds")
        plt.savefig(f'haar_{capture_count}.png')
        print(f"Processing Time: {processing_time:.6f} seconds")
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
        plt.savefig('cascades_bar.png')
    cap.release()
    return average_processing_time
