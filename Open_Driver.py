import cv2
import threading
import msvcrt
import copy
import srt
import numpy as np 
from PIL import Image, ImageDraw,ImageFont 
from pynput import keyboard
from math import floor as mfloor
from math import log as mlog
from time import time as timer
from time import sleep as times
import configparser

#Main Codes
config = configparser.ConfigParser()
config.read('GameConfig.ini')

TrainConf = config['Train']
FilesConf = config['Files']

fileName = str(FilesConf['MainFile'])
StaStart = str(TrainConf['StaStart'])
StaEnd = str(TrainConf['StaEnd'])
StaDistance = str(TrainConf['StaDistance'])
TrainNo = str(TrainConf['TrainNo'])

StartupCheck = False

kch = ''
fps_default = 60
fps = fps_default
fcount = int()
time_delay = 1

frameName = 'Open Driver v1.0 beta'

smooth_play = 50    #1~100
time_delay_margin = 1

speed_mapping = []
signal_mapping = []
#signal_name = ['開車','出發','進站','閉塞','預告','反應燈','信號限速','傾斜式限速','一般限速','接近','停車']
signal_name = ['All Green','Departure','Arrival','Block','Distance','Remote','Signal Speed','Tilt Speed','General Speed','Next Station','Stop']
video_speed = 1   #Real Speed inside video
game_speed = 0   #km/h
vehicle_accel = 0   #km/h/s
vehicle_max = 140   #km/h

distance = StaDistance #meters
distance_passed = 0 #meters

jump_frame = 0

ac_name = ['EB', 'B7', 'B6', 'B5','B4','B3','B2','B1', 'IDLE', 'P1', 'P2', 'P3', 'P4', 'P5']
ac_ctrl = [-4.32, -3.6, -3.1, -2.6, -2.1, -1.6, -1.1, -0.6, 0, 0.5, 0.7, 1.1, 1.3, 1.8]
ac_threshold = [80, 60, 50, 45, 40, 35, 20, 10, 0, 40, 60, 80, 100, 130]
throttle = 8
#0  1  2  3  4  5  6  7    8  9  10 11 12 13
#EB B7 B6 B5 B4 B3 B2 B1 IDLE P1 P2 P3 P4 P5
#-8 -7 -6 -5 -4 -3 -2 -1   0  +1 +2 +3 +4 +5

def on_press(key):
    global kch
    global throttle

    try:
        kch = key.char
    except:
        kch = key.name

    if kch == 'd':
        if throttle + 1 >= 13:
            throttle = 13
        else:
            throttle += 1

    if kch == 'a':
        if throttle - 1 <= 0:
            throttle = 0
        else:
            throttle -= 1


def acclerator():
    global throttle
    global game_speed
    global fps_default
    global speed_mapping
    global video_speed
    global vehicle_accel
    global ac_threshold
    global fps
    global fcount
    global time_delay

    state_stop = True
    factor = 1
    while True:

        video_speed = speed_mapping[mfloor(fcount/fps_default)]

        vehicle_accel = (ac_ctrl[throttle]/smooth_play)
        va = vehicle_accel
        if ac_threshold[throttle] != 0:
            if throttle > 8:
                facX = (game_speed / ac_threshold[throttle])
                factor = (1/1.1)**facX
                print('[ACC]',end='')
            else:
                if game_speed < ac_threshold[throttle]:
                    facX = (game_speed / ac_threshold[throttle]) - 1
                    factor = (1/2)**facX
                    print('[DEC CURVE]',end='')
                else:
                    facX = 1
                    factor = 1
                    print('[DEC FULL]',end='')
        else:
            facX = 1
            factor = 1

        vehicle_accel *= factor

        print("Fixed Acc:"+str(round(vehicle_accel, 5))+" Target Acc:"+str(round(va, 5))+" facX:"+str(round(facX, 5))+" factor:"+str(round(factor, 5)))
        
        game_speed += vehicle_accel
        game_speed = video_speed
        if game_speed <= 0:
            game_speed = 0

        if game_speed >= vehicle_max:
            game_speed = vehicle_max

        game_speed = round(game_speed,3)
        if game_speed != 0:
            fps = (game_speed * fps_default) / video_speed
        else:
            fps = 0

        times(1/smooth_play)

def keyboard_input():
    global kch
    global throttle
    
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
    global vehicle_accel
    global throttle
    global time_delay
    global signal_mapping

    global fcount
    global distance
    global distance_passed
    
    global fileName
    video = cv2.VideoCapture(fileName)
    font = cv2.FONT_HERSHEY_TRIPLEX
    length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    video.set(cv2.CAP_PROP_POS_FRAMES, jump_frame)

    while(video.isOpened()):
        start = timer()
        ret, frame = video.read()
        current_frame = copy.copy(frame)
        if game_speed == 0 or fps <= 1:
            while(game_speed == 0 and fcount > 1) or (fps <= 0.3):
                frame = copy.copy(current_frame)
                cv2.waitKey(1)
                cv2.putText(frame, '['+StaStart+' -> '+StaEnd+'] #'+TrainNo+': ' + str(int(distance) - int(fcount/fps_default)) + 'm',(50, 50), font, 1, (0, 0, 255))
                cv2.putText(frame, 'Throttle: '+ str(ac_name[throttle]) +' Accleration: ' + str(round(vehicle_accel, 5)) + ' Speed:' + str(game_speed)+' km/h',(50, 1000), font, 1, (0, 0, 255))
                cv2.imshow(frameName,frame)

        else:
            y_coord = 400
            time_delay = 1 / fps
            distance_passed += (game_speed*1000/3600)*time_delay
            cv2.putText(frame, '['+StaStart+' -> '+StaEnd+'] #'+TrainNo+': ' + str(int(distance) - int(distance_passed)) + 'm',(50, 50), font, 1, (0, 0, 255))
            cv2.putText(frame, 'Throttle: '+ str(ac_name[throttle]) +' Accleration: ' + str(round(vehicle_accel, 5)) + ' Speed:' + str(game_speed)+' km/h Video Speed: '+str(video_speed)+' km/h', (50, 1000), font, 1, (0, 255, 255))

            if signal_mapping:
                for index, signals in enumerate(signal_mapping[mfloor(fcount/fps_default)]):
                    #print('Index: '+str(index)+' Signal:'+str(signal_name[index])+': '+str(str(signals)))
                    if(signals != 'NULL'):
                        if(signals == 'ALL-RIGHT'):
                            cv2.putText(frame, str(signal_name[index])+': ' + str(signals), (50, y_coord), font, 1, (0, 255, 0))
                        elif(signals == 'CAUTION'):
                            cv2.putText(frame, str(signal_name[index])+': ' + str(signals), (50, y_coord), font, 1, (0, 255, 255))
                        elif(signals == 'DANGER'):
                            cv2.putText(frame, str(signal_name[index])+': ' + str(signals), (50, y_coord), font, 1, (0, 0, 255))
                        else:
                            cv2.putText(frame, str(signal_name[index])+': ' + str(signals), (50, y_coord), font, 1, (255, 0, 255))
                        y_coord += 50
                
            cv2.imshow(frameName, frame)
            cv2.waitKey(1)

            diff = timer() - start
            while  diff < time_delay * 1.04:
                diff = timer() - start

        fcount += 1
        
    video.release()
    cv2.destroyAllWindows()

def parse_text(im, chinese, pos, color):
    img_PIL = Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
    font = ImageFont.truetype('simsun.ttc', 35)
    fillColor = color
    position = pos
    if not isinstance(chinese, str):
        chinese = chinese.decode('utf-8')
    draw = ImageDraw.Draw(img_PIL)
    draw.text(position, chinese, font=font, fill=fillColor)
    img = cv2.cvtColor(np.asarray(img_PIL), cv2.COLOR_RGB2BGR)
    return img


if FilesConf['SpeedMap']:
    try:
        file = open(FilesConf['SpeedMap'])
        line = file.read()
        file.close()
        r = list(srt.parse(line))

        for index, sub in enumerate(r):
            if(index+1 < len(r)):
                for i in range(r[index+1].start.seconds - r[index].start.seconds):
                    speed_mapping.append(float(r[index].content))
            else:
                for i in range(r[index].start.seconds):
                    speed_mapping.append(float(sub.content))

        StartupCheck = True

    except:
        StartupCheck = False
else:
    print('No Speed Mapping Set!')

if FilesConf['SignalMap']:
    try:
        file = open(FilesConf['SignalMap'])
        line = file.read()
        file.close()
        r = list(srt.parse(line))

        for index, sub in enumerate(r):
            if(index+1 < len(r)):
                #print("Sec(Shifted): "+str(r[index+1].start.seconds)+" Speed:"+str(int(r[index].content)))
                for i in range(r[index+1].start.seconds - r[index].start.seconds):
                    signal_mapping.append((r[index].content).split('|'))
            else:
                #print("Sec(Non Shifted): "+str(r[index].start.seconds)+" Speed:"+str(int(sub.content)))
                for i in range(r[index].start.seconds):
                    signal_mapping.append((sub.content).split('-'))

        StartupCheck = True

    except:
        signal_mapping = []


print('Initialized')     

#開車|出發|進站|閉塞|預告|反應燈|信號限速|傾斜式限速|一般限速|接近|停車
#ALL_RIGHT|ALL_RIGHT|NULL|NULL|NULL|NULL|45|45|NULL|NULL

threading.Thread(target = vplayer).start()
threading.Thread(target = acclerator).start()

listener = keyboard.Listener(on_press=on_press)
listener.start()
listener.join()