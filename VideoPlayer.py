import cv2
import time
import threading
import msvcrt

kch = ''
f_ctrl = 1.0
fps_default = 30
video_pause = False

real_speed = 0   #Real Speed inside video
core_speed = 0   #km/h

ac_name = ['EB', 'B7', 'B6', 'B5','B4','B3','B2','B1', 'IDLE', 'P1', 'P2', 'P3', 'P4', 'P5']
ac_ctrl = [-4.32, -3.6, -3.1, -2.6, -2.1, -1.6, -1.1, -0.6, 0, 0.5, 0.7, 1.1, 1.3, 1.8]
throttle = 8
#0  1  2  3  4  5  6  7  8    9  10 11 12 13
#EB B7 B6 B5 B4 B3 B2 B1 IDLE P1 P2 P3 P4 P5
#-8 -7 -6 -5 -4 -3 -2 -1   0  +1 +2 +3 +4 +5

def acclerator():
    global throttle
    global core_speed
    global f_ctrl

    while True:
        print('['+str(ac_name[throttle])+']: '+str(core_speed)+' km/h')
        core_speed += ac_ctrl[throttle]
        if core_speed <= 0:
            core_speed = 0

        if core_speed >= 150:
            core_speed = 150

        f_ctrl = round(core_speed,1)
        time.sleep(1)


def keyboard_input():
    global kch
    global f_ctrl
    global video_pause
    global throttle
    
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


def video_player():
    global kch
    global f_ctrl
    global fps_default
    global video_pause
    global core_speed
    global real_speed
    global throttle

    cap = cv2.VideoCapture("c_full.mp4")
    ret, frame = cap.read()
    frame_buf = frame
    frameName = 'Open Driver v1.0 beta'
    font = cv2.FONT_HERSHEY_SIMPLEX

    fcount = 1
    frameTime = 1

    while(cap.isOpened()):
        ret = cap.grab()
        fcount += 1

        fps = round(fps_default*f_ctrl, 2)

        while(core_speed == 0 and fcount > 1):
            cv2.waitKey(1)
            cv2.putText(frame_buf, 
                    'Fcount: ' + str(fcount) + ' f_ctrl: ' + str("{0:.2f}".format(f_ctrl)), 
                    (50, 50), 
                    font, 0.5, 
                    (0, 255, 255), 
                    2, 
                    cv2.LINE_4)

            cv2.putText(frame_buf, 
                    'Throttle: ' + str(ac_name[throttle]) +') CoreSpeed: '+ str(core_speed) +') RealSpeed: '+str(real_speed), 
                    (50, 100), 
                    font, 0.5, 
                    (0, 255, 255), 
                    2, 
                    cv2.LINE_8)
            cv2.imshow(frameName,frame_buf)

        if fps != 0:
            ret, frame = cap.retrieve()
            frame_buf = frame
            time_delay = round(1/(fps), 2)

            cv2.waitKey(1)
            cv2.putText(frame, 
                    'Fcount: ' + str(fcount) + ' f_ctrl: ' + str("{0:.2f}".format(f_ctrl)), 
                    (50, 50), 
                    font, 0.5, 
                    (0, 255, 255), 
                    2, 
                    cv2.LINE_4)

            cv2.putText(frame, 
                    'Throttle: ' + str(ac_name[throttle]) +') CoreSpeed: '+ str(core_speed) +') RealSpeed: '+str(real_speed), 
                    (50, 100), 
                    font, 0.5, 
                    (0, 255, 255), 
                    2, 
                    cv2.LINE_8)
            cv2.imshow(frameName,frame)
    
            time.sleep(time_delay)

    cap.release()
    cv2.destroyAllWindows()


threading.Thread(target = video_player).start()
threading.Thread(target = keyboard_input).start()
threading.Thread(target = acclerator).start()
