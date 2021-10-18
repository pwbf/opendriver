import numpy as np

FPS = 30

file1 = open('ocr_result.txt', 'r')
Lines = file1.readlines()

def conv_sec(t_sec):
    min, sec = divmod(t_sec, 60)
    hr, min = divmod(min, 60)

    tm = '%02d:%02d:%02d' %(hr, min, sec)
    return tm

speed_old = 0
srt_count = 1

time_se = []
spd_lst = []

tstart = conv_sec(0)
tend = 0

for line in Lines:
    line = line.split(',')
    line[2] = line[2].replace('\n', '')
    frame = int(line[1])
    speed_now = float(line[2])

    tm = conv_sec(int(frame / FPS))
    
    if speed_now != speed_old:
        speed_old = speed_now
        tstart = tm

        time_se.append([tend, tstart])
        spd_lst.append(speed_now)
    else:
        tend = tm
        speed_now = speed_old

time_se = np.roll(time_se, -1)
print(time_se)
for e in range(len(time_se)-1):
    print(str(time_se[e]) + ' -> ' + str(spd_lst[e]))

    print(str(e + 1))
    print(str(time_se[e][0])+',001 --> '+str(time_se[e][1])+',000')
    print(speed_now)
    print()

    with open("421_ttn_yul.srt", "a") as myfile:
        myfile.write(str(e + 1)+'\n')
        myfile.write(str(time_se[e][0])+',001 --> '+str(time_se[e][1])+',000\n')
        myfile.write(str(spd_lst[e])+'\n')
        myfile.write('\n')
