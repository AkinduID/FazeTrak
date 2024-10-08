import cv2
import pyvirtualcam
import numpy as np

cap = cv2.VideoCapture(0)
cam = pyvirtualcam.Camera(width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), fps=30)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Convert BGR to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Send the frame to the virtual camera
    cam.send(frame_rgb)
    cam.sleep_until_next_frame()

    # Show the original frame for debugging (if needed)
    cv2.imshow('Original Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
