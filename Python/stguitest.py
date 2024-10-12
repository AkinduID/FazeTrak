import streamlit as st
import cv2
import numpy as np
import tempfile

# Set the title of the Streamlit app
st.title("Live Webcam Feed")

# Access the webcam
cap = cv2.VideoCapture(0)

# Create a placeholder for the video frame
frame_placeholder = st.empty()
stop_button_pressed = st.button("stop")
# Loop through the video frames
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        st.error("Failed to access webcam. Make sure it's properly connected.")
        break

    # Convert the frame from BGR to RGB (OpenCV uses BGR by default)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Display the frame in Streamlit
    frame_placeholder.image(frame_rgb, channels="RGB")

    # Option to exit the video loop (press 'q' on the keyboard)
    if cv2.waitKey(1) and 0xFF==ord("q") or stop_button_pressed:
        break

# Release the webcam and close the application
cap.release()
