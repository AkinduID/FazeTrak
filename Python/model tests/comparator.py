import funcholistic
import funcblazeface
import funchaar
import funcmtcnn
import funcyolo
import cv2
from pathlib import Path

# define video list
# for each video in video list, 
    # run the face detection functions
    # save each image with the face detection bounding boxes and detection time
    # plot the detection time 
    # save the plot

# holistic_times=funcholistic.holistic_detector('vid1.mp4')
# print(holistic_times)

# cascade_times=funchaar.haar_detector('vid1.mp4')
# print(cascade_times)

mtcnn_times=funcmtcnn.mtcnn_detector('vid1.mp4')
print(mtcnn_times)
