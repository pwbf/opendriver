import cv2
import threading
import msvcrt
import copy
import srt
import numpy as np 
import pathlib
#from PIL import Image, ImageDraw,ImageFont 
from pynput import keyboard
from math import floor as mfloor
from math import log as mlog
from time import time as timer
from time import sleep as times
import datetime
import configparser

#settings
TESTMODE = True
DEBUGLVL = True
JUMPSECS = 2300


#Main Codes
config = configparser.ConfigParser()
config.read('GameConfig.ini')

TrainConf = config['Train']
FilesConf = config['Files']

fileName = str(FilesConf['MainFile'])
StaStart = str(TrainConf['StaStart'])
StaEnd = str(TrainConf['StaEnd'])
StaDistance = str(TrainConf['StaDistance'])
StartTime = str(TrainConf['StartTime'])
TrainNo = str(TrainConf['TrainNo'])

StartupCheck = False

class signalImage:
    def __init__(self):
        self.pathbase = str(pathlib.Path(__file__).parent.resolve())
        self.sl0 = cv2.imread(self.pathbase + '\\asset\\sl0.png', cv2.IMREAD_UNCHANGED)
        self.sl1 = cv2.imread(self.pathbase + '\\asset\\sl1.png', cv2.IMREAD_UNCHANGED)
        self.sl2 = cv2.imread(self.pathbase + '\\asset\\sl2.png', cv2.IMREAD_UNCHANGED)
        self.dep0 = cv2.imread(self.pathbase + '\\asset\\dep0.png', cv2.IMREAD_UNCHANGED)
        self.dep1 = cv2.imread(self.pathbase + '\\asset\\dep1.png', cv2.IMREAD_UNCHANGED)
        self.block0 = cv2.imread(self.pathbase + '\\asset\\block0.png', cv2.IMREAD_UNCHANGED)
        self.block1 = cv2.imread(self.pathbase + '\\asset\\block1.png', cv2.IMREAD_UNCHANGED)
        self.block2 = cv2.imread(self.pathbase + '\\asset\\block2.png', cv2.IMREAD_UNCHANGED)
        self.block3 = cv2.imread(self.pathbase + '\\asset\\block3.png', cv2.IMREAD_UNCHANGED)
        self.dis0 = cv2.imread(self.pathbase + '\\asset\\dis0.png', cv2.IMREAD_UNCHANGED)
        self.dis1 = cv2.imread(self.pathbase + '\\asset\\dis1.png', cv2.IMREAD_UNCHANGED)
        self.dis2 = cv2.imread(self.pathbase + '\\asset\\dis2.png', cv2.IMREAD_UNCHANGED)

kch = ''
fps_default = 60
fps = fps_default
fcount = int()
time_delay = 1

timenow = int(StartTime) + JUMPSECS
timenowH = '00:00:00'

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
idle_factor = -0.2  #km/h/s

distance = StaDistance #meters
distance_passed = 0 #meters

ac_name = ['EB', 'B7', 'B6', 'B5','B4','B3','B2','B1', 'IDLE', 'P1', 'P2', 'P3', 'P4', 'P5']
ac_ctrl = [-4.32, -3.6, -3.1, -2.6, -2.1, -1.6, -1.1, -0.6, 0, 0.5, 0.7, 1.1, 1.3, 1.8]     #km/h/s
ac_threshold = [80, 60, 50, 45, 40, 35, 20, 10, 0, 40, 60, 80, 100, 130]
throttle = 1
#0  1  2  3  4  5  6  7    8  9  10 11 12 13
#EB B7 B6 B5 B4 B3 B2 B1 IDLE P1 P2 P3 P4 P5
#-8 -7 -6 -5 -4 -3 -2 -1   0  +1 +2 +3 +4 +5

def gameTime():
    global timenow
    global timenowH
    while True:
        timenow += 1
        timenowH = str(datetime.timedelta(seconds=timenow))
        times(1)

def on_press(key):
    global kch
    global throttle
    global TESTMODE
    global JUMPSECS

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

    if kch == 't':
        TESTMODE = not TESTMODE
        if(TESTMODE):
            throttle = 8

    #if kch == 'page_down':
        #JUMPSECS += 10000


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
    global TESTMODE

    state_stop = True
    factor = 1
    while True:
        video_speed = speed_mapping[mfloor(fcount/fps_default)]

        vehicle_accel = ((ac_ctrl[throttle] + idle_factor)/smooth_play)
        va = vehicle_accel
        if ac_threshold[throttle] != 0:
            if throttle > 8:
                facX = (game_speed / ac_threshold[throttle])
                factor = (1/1.1)**facX
                #print('[ACC]',end='')
            else:
                if game_speed < ac_threshold[throttle]:
                    facX = (game_speed / ac_threshold[throttle]) - 1
                    factor = (1/2)**facX
                    #print('[DEC CURVE]',end='')
                else:
                    facX = 1
                    factor = 1
                    #print('[DEC FULL]',end='')
        else:
            facX = 1
            factor = 1

        vehicle_accel *= factor

        #print("Fixed Acc:"+str(round(vehicle_accel, 5))+" Target Acc:"+str(round(va, 5))+" facX:"+str(round(facX, 5))+" factor:"+str(round(factor, 5)))
        
        game_speed += vehicle_accel

        if(TESTMODE):
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
    global TESTMODE
    
    lock = threading.Lock()
    while True:
        with lock:
            kch = msvcrt.getch()
            print(kch)
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

            if kch in b't':
                TESTMODE = not bool(TESTMODE)

def frameBlender(x0, y0, simg, frame):
    alphaS = simg[:, :, 3] / 255.0
    alphaF = 1.0 - alphaS

    y1, y2 = y0, y0 + simg.shape[0]
    x1, x2 = x0, x0 + simg.shape[1]

    for c in range(0, 3):
        frame[y1:y2, x1:x2, c] = (alphaS * simg[:, :, c] + alphaF * frame[y1:y2, x1:x2, c])

    return frame

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
    global timenowH
    
    global fileName
    global TESTMODE

    video = cv2.VideoCapture(fileName)
    font = cv2.FONT_HERSHEY_TRIPLEX
    length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    #Fixed current frame if fast forward
    video.set(cv2.CAP_PROP_POS_FRAMES, JUMPSECS * fps_default)
    fcount = JUMPSECS * fps_default

    while(video.isOpened()):
        start = timer()
        ret, frame = video.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2RGBA)

        #Add time now
        cv2.putText(frame, timenowH,(50, 95), font, 1, (0, 0, 0))

        current_frame = copy.copy(frame)

        if game_speed == 0 or fps <= 1:
            while(game_speed == 0 and fcount > 1) or (fps <= 0.3):
                distance_passed = fcount/fps_default
                frame = copy.copy(current_frame)
                cv2.waitKey(1)
                cv2.putText(frame, '['+StaStart+' -> '+StaEnd+'] #'+TrainNo+': ' + str(int(distance) - int(distance_passed)) + 'm',(50, 50), font, 1, (0, 0, 255))
                if(TESTMODE):
                    cv2.putText(frame, '(TESTMODE)(' +str(fcount)+ ') Throttle: '+ str(ac_name[throttle]) +' Accleration: ' + str(round(vehicle_accel, 5)) + ' Speed:' + str(game_speed)+' km/h',(50, 1000), font, 1, (0, 0, 255))
                else:
                    cv2.putText(frame, 'Throttle: '+ str(ac_name[throttle]) +' Accleration: ' + str(round(vehicle_accel, 5)) + ' Speed:' + str(game_speed)+' km/h',(50, 1000), font, 1, (0, 0, 255))
                cv2.imshow(frameName,frame)

        else:
            time_delay = 1 / fps
            distance_passed += (video_speed*1000/3600)*time_delay
            cv2.putText(frame, '['+StaStart+' -> '+StaEnd+'] #'+TrainNo+': ' + str(int(distance) - int(distance_passed)) + 'm',(50, 50), font, 1, (0, 0, 255))
            if(TESTMODE):
                cv2.putText(frame, '(TESTMODE)(' +str(fcount)+ ') Throttle: '+ str(ac_name[throttle]) +' Accleration: ' + str(round(vehicle_accel, 5)) + ' Speed:' + str(game_speed)+' km/h Video Speed: '+str(video_speed)+' km/h', (50, 1000), font, 1, (0, 255, 255))
            else:
                cv2.putText(frame, 'Throttle: '+ str(ac_name[throttle]) +' Accleration: ' + str(round(vehicle_accel, 5)) + ' Speed:' + str(game_speed)+' km/h Video Speed: '+str(video_speed)+' km/h', (50, 1000), font, 1, (0, 255, 255))

            if signal_mapping:
                sg = signalImage()

                #speed limit sign location origin
                slsX = 50
                slsY = 600
                
                #signal location origin
                sigX = 50
                sigY = 100

                #multiple margin
                margin = 10

                #Speed limit sign loc
                tslX = slsX
                tslY = slsY

                gslX = tslX
                gslY = tslY

                #Signal loc

                agX = sigX
                agY = sigY + margin + sg.sl0.shape[0]

                disX = agX + margin + sg.dep0.shape[1]
                disY = agY

                depX = disX + margin + sg.dis0.shape[1]
                depY = disY

                avrX = depX + margin + sg.block0.shape[1]
                avrY = depY

                blockX = avrX + margin + sg.block0.shape[1]
                blockY = avrY

                try:
                    for index, signals in enumerate(signal_mapping[mfloor(fcount/fps_default)]):
                        #print('Index: '+str(index)+' Signal:'+str(signal_name[index])+': '+str(signals))
                        if(signals != 'NULL'):
                            #All Green
                            if(index == 0 and signals != 'NULL'):
                                #print('All Green: '+str(signals))
                                if(signals == 'ALL-RIGHT'):
                                    frame = frameBlender(agX, agY, sg.dep1, frame)

                            #Departure
                            if(index == 1 and signals != 'NULL'):
                                #print('Departure: '+str(signals))
                                if(signals == 'ALL-RIGHT'):
                                    frame = frameBlender(depX, depY, sg.block1, frame)
                                elif(signals == 'CAUTION'):
                                    frame = frameBlender(depX, depY, sg.block2, frame)
                                elif(signals == 'DANGER'):
                                    frame = frameBlender(depX, depY, sg.block3, frame)

                            #Arrival
                            if(index == 2 and signals != 'NULL'):
                                #print('Arrival: '+str(signals))
                                if(signals == 'ALL-RIGHT'):
                                    frame = frameBlender(avrX, avrY, sg.block1, frame)
                                elif(signals == 'CAUTION'):
                                    frame = frameBlender(avrX, avrY, sg.block2, frame)
                                elif(signals == 'DANGER'):
                                    frame = frameBlender(avrX, avrY, sg.block3, frame)

                            #distance signal
                            if(index == 4 and signals != 'NULL'):
                                #print('Distance: '+str(signals))
                                if(signals == 'ALL-RIGHT'):
                                    frame = frameBlender(disX, disY, sg.dis0, frame)
                                elif(signals == 'CAUTION'):
                                    frame = frameBlender(disX, disY, sg.dis1, frame)
                                elif(signals == 'DANGER'):
                                    frame = frameBlender(disX, disY, sg.dis2, frame)
                                
                            #block signal
                            if(index == 3 and signals != 'NULL'):
                                #print('Block: '+str(signals))
                                if(signals == 'ALL-RIGHT'):
                                    frame = frameBlender(blockX, blockY, sg.block1, frame)
                                elif(signals == 'CAUTION'):
                                    frame = frameBlender(blockX, blockY, sg.block2, frame)
                                elif(signals == 'DANGER'):
                                    frame = frameBlender(blockX, blockY, sg.block3, frame)
                            #speed limit
                            if(index == 6 and signals != 'NULL'):  #signal speed
                                if(int(signals) < 100):
                                    cv2.putText(sg.sl1, str(signals),(20, 65), font, 1.5, (0, 0, 0, 255))
                                else:
                                    cv2.putText(sg.sl1, str(signals),(13, 60), font, 1.2, (0, 0, 0, 255))
                                #print('Signal speed')
                                frame = frameBlender(sigX, sigY, sg.sl1, frame)

                            elif((index == 7 and signals != 'NULL') and signal_mapping[mfloor(fcount/fps_default)][8] != 'NULL'):  #seperate track speed
                                if(int(signals) < 100):
                                    cv2.putText(sg.sl2, str(signals),(20, 65), font, 1.5, (0, 0, 0, 255))
                                else:
                                    cv2.putText(sg.sl2, str(signals),(13, 60), font, 1.2, (0, 0, 0, 255))

                                if(int(signal_mapping[mfloor(fcount/fps_default)][8]) < 100):
                                    cv2.putText(sg.sl2, str(signal_mapping[mfloor(fcount/fps_default)][8]),(20, 165), font, 1.5, (0, 0, 0, 255))
                                else:
                                    cv2.putText(sg.sl2, str(signal_mapping[mfloor(fcount/fps_default)][8]),(13, 160), font, 1.2, (0, 0, 0, 255))
                                #print('seperate track speed')
                                frame = frameBlender(tslX, tslY, sg.sl2, frame)
                            elif((index == 7 and signals == 'NULL') and signal_mapping[mfloor(fcount/fps_default)][8] != 'NULL'):  #only general track speed
                                #print('only general track speed')
                                if(int(signals) < 100):
                                    cv2.putText(sg.sl0, str(signals),(20, 65), font, 1.5, (0, 0, 0, 255))
                                else:
                                    cv2.putText(sg.sl0, str(signals),(13, 60), font, 1.2, (0, 0, 0, 255))
                                frame = frameBlender(gslX, gslY, sg.sl0, frame)
                            elif(signal_mapping[7] != 'NULL' and signal_mapping[mfloor(fcount/fps_default)][8] == 'NULL'):  #only tilt track speed(should never reach this part
                                #print('only tilt track speed')
                                if(int(signal_mapping[mfloor(fcount/fps_default)][7]) < 100):
                                    cv2.putText(sg.sl1, str(signal_mapping[mfloor(fcount/fps_default)][7]),(20, 65), font, 1.5, (0, 0, 0, 255))
                                else:
                                    cv2.putText(sg.sl1, str(signal_mapping[mfloor(fcount/fps_default)][7]),(13, 60), font, 1.2, (0, 0, 0, 255))
                                frame = frameBlender(sigX, sigY, sg.sl1, frame)
                except:
                    print('Signal File out of range')
                del sg
                
            cv2.imshow(frameName, frame)
            cv2.waitKey(1)

            diff = timer() - start
            while  diff < time_delay * 1.04:
                diff = timer() - start

        fcount += 1
        
    video.release()
    cv2.destroyAllWindows()
"""
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
"""

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
threading.Thread(target = gameTime).start()

listener = keyboard.Listener(on_press=on_press)
listener.start()
listener.join()