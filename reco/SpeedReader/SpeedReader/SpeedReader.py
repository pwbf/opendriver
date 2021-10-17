#import cupy as cp
import numpy as np
import cv2
from time import time as timer
import sys
import pytesseract
import math

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Administrator\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.'

video = cv2.VideoCapture('a3.mp4')
length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
frameCount = 0

def twistArray(image, deg):
    #start = timer()
    (thresh, image) = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    #image = cp.asarray(image)
    rowcount = 0
    for i in image:
        i = np.roll(i, -3*int((image.shape[1]/2 - rowcount)*math.tan(math.radians(deg))) )
        image[rowcount] = i
        rowcount += 1
    #image = cp.asnumpy(image)
    #print("Time: "+str(timer() - start))
    return image

text = 'N/A'
while(video.isOpened()):
    frameCount += 1
    if video.grab():
        flag, frame = video.retrieve()
        if not flag:
            continue
        else:
            crop_img = frame[965:1150, 100:280]
            crop_img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
            crop_img = twistArray(crop_img, 5)
            text = pytesseract.image_to_string(crop_img, config=custom_config)

            frame = cv2.resize(frame, (1280, 720))
            cv2.putText(frame,'F: ' + str(frameCount), (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
            cv2.imshow('OCR View', crop_img)
            cv2.imshow('Origin', frame)
            cv2.waitKey(1)
            te = str(text.encode("unicode_escape"))
            #print(str(te))
            print('['+str(frameCount)+'('+str(round(frameCount/length * 100, 2))+'%)]-> '+str(text))
            with open("ocr_result.txt", "a") as myfile:
                myfile.write(str(frameCount)+','+te+'\n')
    if cv2.waitKey(10) == 27:
        break

video.release()
cv2.destroyAllWindows()

