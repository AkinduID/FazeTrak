import cv2
import imutils
detector_eye = cv2.CascadeClassifier("cascades/haarcascade_eye.xml")
primary_detector = cv2.CascadeClassifier("cascades/haarcascade_frontalface_alt.xml")
secondary_cascade = cv2.CascadeClassifier("cascades/haarcascade_frontalface_alt2.xml")
tertiary_cascade = cv2.CascadeClassifier("cascades/haarcascade_profileface.xml")
cap = cv2.VideoCapture(0)

while True:
    ret,frame = cap.read()
    if not ret:
        break
    frame = imutils.resize(frame, width=500)
    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faceRects = primary_detector.detectMultiScale(grey, scaleFactor=1.05, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
    for (x, y, w, h) in faceRects:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # eyeRects = detector_eye.detectMultiScale(grey)
        # for (ex, ey, ew, eh) in eyeRects:
        #     cv2.rectangle(frame, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
    if len(faceRects) == 0:
            faces = secondary_cascade.detectMultiScale(grey, 1.1, minSize = (30,30))
            rectColor = (0, 100, 0)
    if len(faceRects) == 0:
            faces = tertiary_cascade.detectMultiScale(grey, 1.1, minSize = (30,30))
            rectColor = (0, 0, 100)
    cv2.imshow("Faces", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()