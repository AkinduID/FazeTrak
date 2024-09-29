import cv2
import matplotlib.pyplot as plt
import IPython.display as display
from IPython.display import clear_output
import time
from ultralytics import YOLO

def yolo_detector(cap):

    yolo = YOLO('yolov8s.pt')

    # Function to get class colors
    def getColours(cls_num):
        base_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        color_index = cls_num % len(base_colors)
        increments = [(1, -2, 1), (-2, 1, -1), (1, -1, 2)]
        color = [base_colors[color_index][i] + increments[color_index][i] * 
        (cls_num // len(base_colors)) % 256 for i in range(3)]
        return tuple(color)

    # For tracking processing times
    processing_times = []
    capture_count = 0

    # Start the loop to capture and process frames
    start_time = time.time()

    while capture_count < 11:  # Limit to 11 frames 
        ret, frame = cap.read()
        if not ret:
            continue

        # Start time of processing for current frame
        frame_start_time = time.perf_counter()

        # Run YOLOv8 tracking
        results = yolo.track(frame, stream=True)

        for result in results:
            # Get the class names
            classes_names = result.names

            # Iterate over each detection box
            for box in result.boxes:
                # Check if confidence is greater than 40 percent
                if box.conf[0] > 0.4:
                    # Get bounding box coordinates
                    [x1, y1, x2, y2] = box.xyxy[0]
                    # Convert to integers
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                    # Get the class ID
                    cls = int(box.cls[0])

                    # Get the class name
                    class_name = classes_names[cls]

                    # Get the respective color for the class
                    colour = getColours(cls)

                    # Draw the rectangle on the frame
                    cv2.rectangle(frame, (x1, y1), (x2, y2), colour, 2)

                    # Put the class name and confidence on the frame
                    cv2.putText(frame, f'{class_name} {box.conf[0]:.2f}', (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, colour, 2)

        # Measure the end time of processing for the current frame
        frame_end_time = time.perf_counter()

        # Calculate processing time for this frame
        processing_time = frame_end_time - frame_start_time

        # Store the processing time after the first frame
        if capture_count > 0:
            processing_times.append(processing_time)

        capture_count += 1

        # Convert the frame from BGR to RGB (for displaying in matplotlib)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Clear previous output and display the current frame with processing time
        clear_output(wait=True)
        plt.imshow(frame_rgb)
        plt.axis('off')
        plt.title(f"Processing Time: {processing_time:.6f} seconds")
        plt.show()

        # Break if 'q' is pressed (you can add an optional manual exit)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Calculate and display average processing time
        if processing_times:
            avg_processing_time = sum(processing_times) / len(processing_times)
            print(f"Average Processing Time (excluding first frame): {avg_processing_time:.6f} seconds")
