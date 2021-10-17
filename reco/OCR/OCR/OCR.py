import pytesseract
import cv2
import os
import numpy as np
import math

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Administrator\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.'

image=cv2.imread('frame.png')
(thresh, image) = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
#image=cv2.imread('number.png')

def twistArray(image, deg):
    rowcount = 0
    for i in image:
        #print("r=%03d m=%03d "%( rowcount , int((image.shape[1]/2 - rowcount)*math.tan(math.radians(deg))) ), end="")
        i = np.roll(i, -3*int((image.shape[1]/2 - rowcount)*math.tan(math.radians(deg))) )
        image[rowcount] = i
        rowcount += 1
        #for j in i:
            #if np.array_equal(j, [255,255,255]):
                #print('_', end="")
            #if np.array_equal(j, [0,0,0]):
                #print('I', end="")
        #print()
    return image

image = twistArray(image,20)
cv2.imshow('OCR View', image)
cv2.waitKey(1)
text = pytesseract.image_to_string(image, config = custom_config)
print(text)

while(True):
    a=1