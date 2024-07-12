import sys
import time
import datetime
import threading

STEP = 20
TIME_INTERVAL = 5
FIRST_DUTY_CYCLE = 100

start_time = datetime.datetime.now().time() # time object
coordinates = dict()
operations_list = list()

def distance_table(speed):
    """ distance depending_on_speed
        - speed steps are from 20 to 20
        - distance is in cm """
    if (speed == 0):
        distance_forward = 0
        distance_backward = 0
    elif (speed == STEP): #20%
        distance_forward = 2.58
        distance_backward = 1.68
    elif (speed == STEP*2): #40%
        distance_forward = 6.32
        distance_backward = 3.78
    elif (speed == STEP*3): #60%
        distance_forward = 9.24
        distance_backward = 6.84
    elif (speed == STEP*4): #80%
        distance_forward = 13.86
        distance_backward = 9.44
    elif (speed == STEP*5): #100%
        distance_forward = 18.96
        distance_backward = 10.94
    else:
        print('not valid')

    return distance_forward, distance_backward

def distance_travelled(direction, speed, time):
    time_coeficient = 0.1
    distance_forward, distance_backward = distance_table(speed)

    if (direction == 'f'):
        distance = (time * distance_forward) / time_coeficient
    elif (direction == 'b'):
        distance = - (time * distance_backward) / time_coeficient
    elif (direction == 's'):
        distance = (time * distance_forward) / time_coeficient
    
    #time.sleep(TIME_INTERVAL)

    print(distance)
    return distance

def update_coordinates(coordinates, data, speed, time):
    distance = distance = distance_travelled(data, speed, time)

    if coordinates['orientation'] == 'N':
        coordinates['y'] += distance
    elif coordinates['orientation'] == 'S':
        coordinates['y'] -= distance
    elif coordinates['orientation'] == 'E':
        coordinates['x'] += distance
    elif coordinates['orientation'] == 'W':
        coordinates['x'] -= distance
    
    print(coordinates)

def var_speed(speed, step):
    speed = speed + step
    if (speed < 0):
        speed = 0
        print ('limits exceeded - invalid speed')
    elif (speed > 100):
        speed = 100
    """ else:
        pwm_control.ChangeDutyCycle(speed) """
    return speed

def dateToTime(tm):
    fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    return fulldate.time()

def addSecs(tm, secs):
    fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    fulldate = tm + datetime.timedelta(seconds=secs)
    return fulldate.time()

def get_location(coordinates, request_time):
    for i in range(len(operations_list)):
        if i == len(operations_list)-1:
            if addSecs(operations_list[i]['op_start'], TIME_INTERVAL) <= dateToTime(request_time) and operations_list[i]['op_start'] == operations_list[i]['new_op_start']: #reading of location after last operation
                print("IF")
                update_coordinates(coordinates, operations_list[i]['op_type'], operations_list[i]['speed'], TIME_INTERVAL)
                operations_list.pop(i)
            #elif addSecs(operations_list[i]['op_start'], TIME_INTERVAL) <= dateToTime(request_time) and operations_list[i]['op_start'] != operations_list[i]['new_op_start']:
            else: #reading of location during last operation
                print("ELSE")
                time = (request_time - operations_list[i]['new_op_start']).total_seconds()
                print(time) #request time is changing, need fix 
                update_coordinates(coordinates, operations_list[i]['op_type'], operations_list[i]['speed'], time)
                print(operations_list)
                operations_list[i]['new_op_start'] = request_time
                print(operations_list)
        #else:
        #if addSecs(operations_list[i]['op_time'], TIME_INTERVAL) <= dateToTime(operations_list[i+1]['op_time']):
    


def main(argv):
    #python3 test.py x y N/S/E/W
    coordinates={'x': float(argv[1]), 'y': float(argv[2]), 'orientation': argv[3], 't': start_time}
    #print(start_time)
    print(coordinates)

    speed = 100

    lock = threading.Lock()

    while 1:
        data = input()

        op_start = datetime.datetime.now()

        if data == '1':
            print('turn_on()')
        elif data == '0':
            print('turn_off()')
        elif data == 'f':
            print('forward')
            operations_list.append({'op_type': data, 'speed': speed, 'op_start': op_start, 'op_finish': addSecs(op_start, TIME_INTERVAL), 'new_op_start': op_start})
            #tf = threading.Thread(target=update_coordinates, args=(coordinates, data, speed,))
            #tf.start()
        elif data == 'b':
            print('backward')
            operations_list.append({'op_type': data, 'speed': speed, 'op_start': op_start, 'op_finish': addSecs(op_start, TIME_INTERVAL), 'new_op_start': op_start})
            #tb = threading.Thread(target=update_coordinates, args=(coordinates, data, speed,))
            #tb.start()
        elif data == 's':
            print('stop')
            speed = 0
            operations_list.append({'op_type': data, 'speed': speed, 'op_start': op_start, 'op_finish': addSecs(op_start, TIME_INTERVAL), 'new_op_start': op_start})
            #ts = threading.Thread(target=update_coordinates, args=(coordinates, data, speed,))
            #ts.start()
        elif data == 'u':
            tu = threading.Thread(target=get_location, args=(coordinates, op_start,))
            tu.start()
            tu.join()
        elif data == 'i':
            #increase speed
            speed = var_speed(speed, STEP)
            operations_list.append({'op_type': data, 'speed': speed, 'op_start': op_start, 'op_finish': addSecs(op_start, TIME_INTERVAL), 'new_op_start': op_start})
            print ('new speed ', speed)
        elif (data =='d'):
            #decrease speed
            speed = var_speed(speed, -STEP)
            operations_list.append({'op_type': data, 'speed': speed, 'op_start': op_start, 'op_finish': addSecs(op_start, TIME_INTERVAL), 'new_op_start': op_start})
            print ('new speed ', speed)
        else:
            print('not valid')
            
if __name__=="__main__":
    try:
        main(sys.argv[0:])
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)