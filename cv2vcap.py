#import numpy as np
import cv2
from time import time as timer
import sys

video = cv2.VideoCapture('5M30FPS.mp4')
fps = video.get(cv2.CAP_PROP_FPS)
print(fps)
fps /= 1000
framerate = timer()
elapsed = int()
cv2.namedWindow('ca1', 0)
while(video.isOpened()):

    start = timer()
    # print(start)
    ret, frame = video.read()
    cv2.putText(frame,'elapsed: ' + str(elapsed), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255))
    cv2.imshow('ca1',frame)
    cv2.waitKey(1)

    diff = timer() - start
    while  diff < (1/30):
        diff = timer() - start

    elapsed += 1
    

video.release()
cv2.destroyAllWindows()
