import cv2
import imutils
detector_eye = cv2.CascadeClassifier("cascades/haarcascade_eye.xml")
detector = cv2.CascadeClassifier("cascades/haarcascade_frontalface_default.xml")
cap = cv2.VideoCapture(1)

while True:
    ret,frame = cap.read()
    if not ret:
        break
    frame = imutils.resize(frame, width=500)
    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faceRects = detector.detectMultiScale(grey, scaleFactor=1.05, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
    for (x, y, w, h) in faceRects:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        eyeRects = detector_eye.detectMultiScale(grey)
        for (ex, ey, ew, eh) in eyeRects:
            cv2.rectangle(frame, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
    cv2.imshow("Faces", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()