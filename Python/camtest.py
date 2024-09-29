import cv2

# Start with an arbitrary camera index (e.g., 0)
camera_index = 0

while True:
  # Create a VideoCapture object
  cap = cv2.VideoCapture(camera_index)

  # Check if the camera opened successfully
  if cap.isOpened():
    print(f"Camera {camera_index} is available.")
    cap.release()  # Release the camera resource
    camera_index += 1  # Move to the next camera
  else:
    # Camera not found, break the loop
    break

print("No more cameras found.")