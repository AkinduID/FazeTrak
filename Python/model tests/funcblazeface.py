import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import matplotlib.pyplot as plt
from IPython.display import clear_output
import time
from pathlib import Path

BaseOptions = mp.tasks.BaseOptions
FaceDetector = mp.tasks.vision.FaceDetector
FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
FaceDetectorResult = mp.tasks.vision.FaceDetectorResult
VisionRunningMode = mp.tasks.vision.RunningMode
# Ensure the correct absolute path for the model
model_path = Path(r"D:\Documents\Campus\S5\2 - Embedded Systems Project\Repo\Face-Tracking-WebCam\Python\model tests\blaze_face_short_range.tflite")

latest_result = None

def blazeface_detector(video):
    def print_result(result, output_image: mp.Image, timestamp_ms: int):
        global latest_result
        latest_result = result
    
    options = FaceDetectorOptions(
        base_options=BaseOptions(model_asset_path=str(model_path)),  # Update with correct model path
        running_mode=VisionRunningMode.LIVE_STREAM,
        min_detection_confidence=0.5,
        min_suppression_threshold=0.3,
        result_callback=print_result
    )

    with FaceDetector.create_from_options(options) as detector:
        cap = cv2.VideoCapture(video)
        processing_times = []
        capture_count = 0
        StartTime = time.time()
        
        while cap.isOpened() and capture_count < 11:
            ret, frame = cap.read()
            if not ret:
                break
            start_time=time.perf_counter()
            timestamp_ms = int((time.time() - StartTime) * 1000)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            detector.detect_async(mp_image, timestamp_ms)

            if latest_result:
                for detection in latest_result.detections:
                    bbox = detection.bounding_box
                    start_point = (int(bbox.origin_x), int(bbox.origin_y))
                    end_point = (int(bbox.origin_x + bbox.width), int(bbox.origin_y + bbox.height))
                    color = (0, 255, 0)
                    thickness = 2
                    cv2.rectangle(frame, start_point, end_point, color, thickness)

            frame_end_time = time.perf_counter()
            processing_time = frame_end_time - start_time
            if capture_count > 0:
                processing_times.append(processing_time)

            capture_count += 1
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            clear_output(wait=True)
            plt.imshow(image_rgb)
            plt.axis('off')
            plt.title(f"Processing Time: {processing_time:.6f} seconds")
            # plt.show()
            plt.savefig(f'blazeface_{capture_count}.png')
            print(f"Processing Time: {processing_time:.6f} seconds")

            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break

        if processing_times:
            average_processing_time = sum(processing_times) / len(processing_times)
            print(f"Average Processing Time (excluding first capture): {average_processing_time:.6f} seconds")
            plt.clf()
            plt.bar(range(len(processing_times)), processing_times, color='blue')
            plt.xlabel('Frame')
            plt.ylabel('Time(s)')
            plt.title('Time to detect face in frame')
            plt.savefig('blazeface_bar.png')
    cap.release()
    print(processing_times)
    return average_processing_time

li=blazeface_detector('vid1.mp4')