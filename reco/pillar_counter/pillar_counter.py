import cv2
import numpy as np

templates = []
for i in range(12):
    templates.append(cv2.imread('Image00'+str(i+6)+'.png',0))

threshold = 0.7
img_rgb  = cv2.imread('Image018.png')
img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
prev_index = 0
for index,template in enumerate(templates):
    prev_index = index
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
    loc = list(np.where(res >= threshold))

    for pt in zip(*loc[::-1]):
        cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,255,255), 2)
    
    print('> '+str(index)+' <' + str(loc))

cv2.imshow('Detected',img_rgb)
while True:
    cv2.waitKey(1)

#video = cv2.VideoCapture('sample.mp4')
#while(video.isOpened()):
#    ret, frame = video.read()
#    if ret:
#        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#        for template in templates:
#            w, h = template.shape[::-1]
#            res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
#            loc = np.where(res >= threshold)

#            for pt in zip(*loc[::-1]):
#                cv2.rectangle(frame, pt, (pt[0] + w, pt[1] + h), (0,255,255), 2)

#        cv2.imshow('Detected',frame)
#        cv2.waitKey(1)
#    else:
#        break
print("Ended")