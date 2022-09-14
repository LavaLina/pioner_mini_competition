import time
import math
import numpy as np
import cv2 as cv

from pioneer_sdk import Pioneer
import multiprocessing as mp
from multiprocessing.managers import BaseManager

#i = 0     1    2    3    4   5
x = [0.0, 0.4, 0.4, 0.0, 0.0, 0]
y = [0.5, 0.5, 0.7, 0.7, 0.5, 0]
command_yaw = math.radians(float(0))

def take_photo(buff, drone):
    new_message = False
    while True:
        try:
            frame = cv.imdecode(np.frombuffer(drone.get_raw_video_frame(), dtype=np.uint8),
                                        cv.IMREAD_COLOR)

            if not buff.empty():
                message = buff.get()
                if len(message) == 1 and message[0] == 'end':
                    break
                i = message[0]
                new_message = True

            if new_message:
                name = "frame" + str(i) + "_" + str(x[i]) + "_" + str(y[i]) + ".jpg"
                cv.imwrite(name, frame)

                new_message = False

        except cv.error:
            continue

        cv.imshow('pioneer_camera_stream', frame)

        key = cv.waitKey(1)
        if key == 27:
            print('esc pressed')
            drone.land()
            break


def drone_control(buff, drone):
    new_point = True

    i = 0

    command_x = x[i]
    command_y = y[i]
    command_z = float(1)
    command_yaw = math.radians(float(0))

    if buff.full():
        buff.get()

    buff.put([i])

    while True:
        if new_point:
            print("Летим в точку ", command_x, ", ", command_y, ", ", command_z)
            drone.go_to_local_point(x=command_x, y=command_y, z=command_z, yaw=command_yaw)
            new_point = False

        key = cv.waitKey(1)
        if key == 27:
            print('esc pressed')
            pioneer_mini.land()

            if buff.full():
               buff.get()
            buff.put(['end'])
            break

        time.sleep(5)

        print("Достигнута точка ", command_x, ", ", command_y, ", ", command_z)

        if buff.full():
            buff.get()
        buff.put([i])

        i = i + 1

        if i < len(x):
            command_x = x[i]
            command_y = y[i]
            time.sleep(2)
            new_point = True
        else:
            drone.land()
            if buff.full():
                buff.get()
            buff.put(['end'])
            break

if __name__ == '__main__':
    BaseManager.register('Pioneer', Pioneer)
    manager = BaseManager()
    manager.start()
    pioneer_mini = manager.Pioneer()
    pioneer_mini.arm()
    pioneer_mini.takeoff()

    buffer = mp.Queue(maxsize=1)

    photo_taker = mp.Process(target=take_photo, args=(buffer, pioneer_mini))
    flight_navigator = mp.Process(target=drone_control, args=(buffer, pioneer_mini))

    photo_taker.start()
    flight_navigator.start()

    photo_taker.join()
    flight_navigator.join()

    pioneer_mini.land()
