import cv2
from time import time as timer
from time import sleep as times
import threading
import msvcrt
import copy
import srt
from math import floor as mfloor

kch = ''
fps_default = 30
fps = fps_default
fcount = int()
time_delay = 1

fileName = "d_c3.mp4"
frameName = 'Open Driver v1.0 beta'

smooth_play = 100    #1~100
time_delay_margin = 1

speed_mapping = []
video_speed = 1   #Real Speed inside video
game_speed = 0   #km/h

distance = 6400 #meters
distance_passed = 0 #meters

ac_name = ['EB', 'B7', 'B6', 'B5','B4','B3','B2','B1', 'IDLE', 'P1', 'P2', 'P3', 'P4', 'P5']
ac_ctrl = [-4.32, -3.6, -3.1, -2.6, -2.1, -1.6, -1.1, -0.6, 0, 0.5, 0.7, 1.1, 1.3, 1.8]
throttle = 8
#0  1  2  3  4  5  6  7    8  9  10 11 12 13
#EB B7 B6 B5 B4 B3 B2 B1 IDLE P1 P2 P3 P4 P5
#-8 -7 -6 -5 -4 -3 -2 -1   0  +1 +2 +3 +4 +5


def acclerator():
    global throttle
    global game_speed
    global fps_default
    global speed_mapping
    global video_speed
    global fps
    global fcount
    global time_delay

    while True:
        video_speed = speed_mapping[mfloor(fcount/fps_default)]
        game_speed += (ac_ctrl[throttle]/smooth_play)
        if game_speed <= 0:
            game_speed = 0

        if game_speed >= 150:
            game_speed = 150

        game_speed = round(game_speed,3)

        if game_speed != 0:
            fps = (game_speed * fps_default) / video_speed
        else:
            fps = 0

        #if fps!=0:
            #print('['+str(ac_name[throttle])+']: '+str(game_speed)+' km/h fps:'+str(fps)+' time_delay: '+str(time_delay))
        #else:
            #print('['+str(ac_name[throttle])+']: '+str(game_speed)+' km/h fps:'+str(fps)+' time_delay: Stationary')
        times(1/smooth_play)

def keyboard_input():
    global kch
    global throttle
    global fps
    
    lock = threading.Lock()
    while True:
        with lock:
            kch = msvcrt.getch()
            #print(kch)
            if kch in b'd':
                if throttle + 1 >= 13:
                    throttle = 13
                else:
                    throttle += 1

            if kch in b'a':
                if throttle - 1 <= 0:
                    throttle = 0
                else:
                    throttle -= 1

def vplayer():
    global kch
    global fps
    global game_speed
    global video_speed
    global throttle
    global time_delay

    global fcount
    global distance
    global distance_passed
    
    global fileName
    video = cv2.VideoCapture(fileName)
    font = cv2.FONT_HERSHEY_SIMPLEX

    while(video.isOpened()):
        start = timer()
        ret, frame = video.read()
        current_frame = copy.copy(frame)

        if game_speed == 0 or fps <= 1:
            while(game_speed == 0 and fcount > 1) or (fps <= 0.3):
                frame = copy.copy(current_frame)
                cv2.waitKey(1)
                cv2.putText(frame, '[Taipei -> Songshan] #408: ' + str(distance - int(fcount/fps_default)) + 'm, fps:' + str(fps),(50, 20), font, 0.5, (0, 0, 255))
                cv2.putText(frame, '[Stationary] Fcount: ' + str(fcount) + ' fps:' + str(fps)  + ' TM: stationary',(50, 50), font, 0.5, (0, 0, 255))
                cv2.putText(frame, 'Throttle: ' + str(ac_name[throttle]) +' CoreSpeed: '+ str(game_speed) +' video_speed: '+str(video_speed), (50, 100), font, 0.5, (0, 0, 255))
                cv2.imshow(frameName,frame)

        else:
            time_delay = 1 / fps
            distance_passed += game_speed*1000/3600*time_delay
            cv2.putText(frame, '[Taipei -> Songshan] #408: ' + str(distance - int(distance_passed)) + 'm, fps:' + str(fps),(50, 20), font, 0.5, (0, 255, 255))
            cv2.putText(frame, '[Moving] Fcount: ' + str(fcount) + ' fps:' + str(fps)  + ' TM: '+str(mfloor(fcount/fps_default)),(50, 50), font, 0.5, (0, 255, 255))
            cv2.putText(frame, 'Throttle: ' + str(ac_name[throttle]) +' CoreSpeed: '+ str(game_speed) +' video_speed: '+str(video_speed), (50, 100), font, 0.5, (0, 255, 255))
                
            cv2.imshow(frameName, frame)
            cv2.waitKey(1)

            diff = timer() - start
            while  diff < time_delay:
                diff = timer() - start

        fcount += 1
        
    video.release()
    cv2.destroyAllWindows()

file = open("408_TPE_SOH.srt")
line = file.read()
file.close()
r = list(srt.parse(line))

for index, sub in enumerate(r):
    if(index+1 < len(r)):
        print("Sec(Shifted): "+str(r[index+1].start.seconds)+" Speed:"+str(int(r[index].content)))
        for i in range(r[index+1].start.seconds - r[index].start.seconds):
            speed_mapping.append(int(r[index].content))
    else:
        print("Sec(Non Shifted): "+str(r[index].start.seconds)+" Speed:"+str(int(sub.content)))
        for i in range(r[index].start.seconds):
            speed_mapping.append(int(sub.content))

#print(speed_mapping)            
print('Initialized')            


threading.Thread(target = vplayer).start()
threading.Thread(target = keyboard_input).start()
threading.Thread(target = acclerator).start()
