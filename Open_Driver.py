import cv2
import time
import threading
import msvcrt
import copy
import srt

kch = ''
fps_default = 300
fps = fps_default
fcount = 1
time_delay = 1

smooth_play = 100    #1~100
time_delay_margin = 1

speed_mapping = []
video_speed = 1   #Real Speed inside video
game_speed = 0   #km/h

distance = 6400 #meters

ac_name = ['EB', 'B7', 'B6', 'B5','B4','B3','B2','B1', 'IDLE', 'P1', 'P2', 'P3', 'P4', 'P5']
ac_ctrl = [-4.32, -3.6, -3.1, -2.6, -2.1, -1.6, -1.1, -0.6, 0, 0.5, 0.7, 1.1, 1.3, 1.8]
throttle = 0
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
        video_speed = speed_mapping[int(fcount/fps_default)]
        game_speed += (ac_ctrl[throttle]/smooth_play)
        if game_speed <= 0:
            game_speed = 0

        if game_speed >= 150:
            game_speed = 150

        game_speed = round(game_speed,3)

        if game_speed != 0:
            fps = (game_speed * fps_default) / video_speed
            #fps = game_speed*40
        else:
            fps = 0

        #if fps!=0:
            #print('['+str(ac_name[throttle])+']: '+str(game_speed)+' km/h fps:'+str(fps)+' time_delay: '+str(time_delay))
        #else:
            #print('['+str(ac_name[throttle])+']: '+str(game_speed)+' km/h fps:'+str(fps)+' time_delay: Stationary')
        time.sleep(1/smooth_play)

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


def frame_player():
    global kch
    global fps
    global game_speed
    global video_speed
    global throttle
    global time_delay

    global fcount
    global distance
    global cap

    cap = cv2.VideoCapture("d_c2.mp4")
    cap.set(cv2.CAP_PROP_FPS, fps_default)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    
    frameName = 'Open Driver v1.0 beta'
    font = cv2.FONT_HERSHEY_SIMPLEX

    fcount = 1
    frameTime = 1
    frame_spd = 1.0
    
    while(cap.isOpened()):
        ret, frame = cap.read()
        current_frame = frame
        ts = time.time()
        ret = cap.grab()
        fcount += 1

        if game_speed == 0 or fps <= 1:
            while(game_speed == 0 and fcount > 1) or (fps <= 0.3):
                frame = copy.copy(current_frame)
                cv2.waitKey(1)
                cv2.putText(frame, '[Taipei -> Songshan] #408: ' + str(distance - int(fcount/300)) + 'm, fps:' + str(fps),(50, 20), font, 0.5, (0, 0, 255))
                cv2.putText(frame, '[Stationary] Fcount: ' + str(fcount) + ' fps:' + str(fps)  + ' TM: stationary',(50, 50), font, 0.5, (0, 0, 255))
                cv2.putText(frame, 'Throttle: ' + str(ac_name[throttle]) +' CoreSpeed: '+ str(game_speed) +' video_speed: '+str(video_speed), (50, 100), font, 0.5, (0, 0, 255))
                #cv2.putText(frame, 'Throttle: ' + str(ac_name[throttle]) +' CoreSpeed: '+ str(game_speed), (50, 100), font, 0.5, (0, 0, 255))
                cv2.imshow(frameName,frame)

        else:

            frame_spd = round(fps / fps_default, 4)
            if frame_spd <= 1.1:
                #ret, frame = cap.read()
                current_frame = copy.copy(frame)
                time_delay = 1 / fps
            
                cv2.waitKey(1)
                cv2.putText(frame, '[Taipei -> Songshan] #408: ' + str(distance - int(fcount/300)) + 'm, fps:' + str(fps),(50, 20), font, 0.5, (0, 255, 255))
                cv2.putText(frame,'[Moving] Fcount: ' + str(fcount) + ' fps:' + str(fps) + ' TM:' + str(time_delay), (50, 50), font, 0.5, (0, 255, 255))
                if throttle <8:
                    cv2.putText(frame,'Throttle: ' + str(ac_name[throttle]) +' CoreSpeed: '+ str(game_speed) +' video_speed: '+str(video_speed), (50, 100),font, 0.5, (0, 0, 255))
                elif throttle ==8:
                    cv2.putText(frame,'Throttle: ' + str(ac_name[throttle]) +' CoreSpeed: '+ str(game_speed) +' video_speed: '+str(video_speed), (50, 100),font, 0.5, (0, 255, 255))
                elif throttle >8:
                    cv2.putText(frame,'Throttle: ' + str(ac_name[throttle]) +' CoreSpeed: '+ str(game_speed) +' video_speed: '+str(video_speed), (50, 100),font, 0.5, (255, 255, 0))
                #cv2.putText(frame, 'Throttle: ' + str(ac_name[throttle]) +' CoreSpeed: '+ str(game_speed), (50, 100), font, 0.5, (0, 255, 255))
                cv2.imshow(frameName,frame)
                ret = cap.grab()

                te = time.time()
                print('[DELAY] T Elaps:', str(te-ts))

            else:
                if (fcount) % int((frame_spd - 1)*10) == 0:
                    cv2.waitKey(1)
                    cv2.putText(frame, '[Taipei -> Songshan] #408: ' + str(distance - int(fcount/300)) + 'm, fps:' + str(fps),(50, 20), font, 0.5, (0, 255, 255))
                    cv2.putText(frame,'[Moving] Fcount: ' + str(fcount) + ' fps:' + str(fps) + ' TM:' + str(time_delay), (50, 50), font, 0.5, (0, 255, 255))
                    if throttle <8:
                        cv2.putText(frame,'Throttle: ' + str(ac_name[throttle]) +' CoreSpeed: '+ str(game_speed) +' video_speed: '+str(video_speed), (50, 100),font, 0.5, (0, 0, 255))
                    elif throttle ==8:
                        cv2.putText(frame,'Throttle: ' + str(ac_name[throttle]) +' CoreSpeed: '+ str(game_speed) +' video_speed: '+str(video_speed), (50, 100),font, 0.5, (0, 255, 255))
                    elif throttle >8:
                        cv2.putText(frame,'Throttle: ' + str(ac_name[throttle]) +' CoreSpeed: '+ str(game_speed) +' video_speed: '+str(video_speed), (50, 100),font, 0.5, (255, 255, 0))
                    #cv2.putText(frame, 'Throttle: ' + str(ac_name[throttle]) +' CoreSpeed: '+ str(game_speed), (50, 100), font, 0.5, (0, 255, 255))
                    cv2.imshow(frameName,frame)
                    ret = cap.grab()
                    te = time.time()
                    print('[SKIP] T Elaps:'+ str(te-ts)+' Fcount:'+str(fcount)+' fspd:'+str(frame_spd))
                else:
                    continue
    
    cap.release()
    cv2.destroyAllWindows()

file = open("408_TPE_SOH.srt")
line = file.read()
file.close()
r = list(srt.parse(line))

for sub in r:
    sec_now = sub.start.seconds
    if sec_now > 0:
        for i in range(sec_now):
            speed_mapping.append(int(sub.content))
            

threading.Thread(target = frame_player).start()
threading.Thread(target = keyboard_input).start()
threading.Thread(target = acclerator).start()
