from yolov5n import *
import numpy as np

class Kiwicar:
    def __init__(self, msf, mrt, base_speed):
        self.base_speed = base_speed
        self.max_steering = 38 * np.pi/180
        self.groundSteering = 0
        self.pedalPosition = 0
        self.in_reverse = False
        self.max_stillstanding_frames = msf
        self.max_reverse_time = mrt
        self.reverse_time = 0
        self.still_standing_frames = 0
        self.zero_detections = True
        self.data = []
        self.terminate = False
        self.front_dist_list = []
        self.turning = False
        self.max_turn_duration = 2
    def append_data(self):
        a = np.asarray(self.data)
        np.savetxt("Reverse_data.csv", a, delimiter=",", fmt='%s')
    
    def get_state(self):
        return self.groundSteering, self.pedalPosition
    
    def no_obstacles(self, dist_front):
        if dist_front > 0 and dist_front < 0.2:
            self.groundSteering = 0
            self.pedalPosition = 0
            return False
        else:
            return True

    def search(self, dist_front):
        if dist_front > 0 and dist_front < 0.5:
            self.turning = True
            self.initiate_turn()
        else:
            self.groundSteering, self.pedalPosition = 0, self.base_speed


    def followkiwi(self, img):
        detections = pre_process(img, net)
        self.groundSteering, self.pedalPosition, self.zero_detections = post_process(img, detections, self.base_speed, self.max_steering)

    def initiate_reverse(self, dist_rear):
        self.still_standing_frames = 0
        self.in_reverse = True
        self.reverse(dist_rear)

    def initiate_turn(self):
        self.groundSteering, self.pedalPosition = self.max_steering , self.base_speed+0.01
        self.turn_duration = 0
        self.turn()

    def turn(self):
        self.turn_duration += 0.1
        if self.turn_duration >= self.max_turn_duration:
            self.turning = False

    def reverse(self, dist_rear):
        self.data.append('Trying to reverse')
        if self.reverse_time >= self.max_reverse_time:
            self.in_reverse = False
            self.reverse_time = 0
            self.groundSteering = 0
            self.pedalPosition = 0
            self.data.append(f'Reverse: {self.reverse_time} greater than max so reverse completed')
            self.terminate = True
        if dist_rear > 0.1 or dist_rear == 0:
            self.groundSteering = 0
            self.pedalPosition = -0.4
            self.reverse_time += 0.1
            self.data.append(f'Reversing: time is {self.reverse_time}')
        else:
            self.in_reverse = False
            self.reverse_time = 0
            self.groundSteering = 0
            self.pedalPosition = 0
            self.data.append(f'Cant reverse anymore because dist rear is {dist_rear}')
            self.terminate = True

    def getUnstuck(self, front_dist, rear_dist):
        front_dist = round(front_dist,5)
        if len(self.front_dist_list) < 5:
            self.front_dist_list.append(front_dist)
        else:
            if (self.front_dist_list.count(self.front_dist_list[0] == len(self.front_dist_list))):
                self.initiate_reverse(rear_dist)
            self.front_dist_list.append(front_dist)
            self.front_dist_list.pop(0)


    def move(self, img, dist_front, dist_rear):
        if self.in_reverse:
            self.reverse(dist_rear)
            return
        
        if self.no_obstacles(dist_front):
            if self.turning:
                self.turn()
                return
        
            self.followkiwi(img)

            if self.zero_detections:
                self.search(dist_front)

        # self.getUnstuck(dist_front, dist_rear)

        # Reverse if kiwicar gets stuck.
        if self.pedalPosition == 0 and self.zero_detections:
            if self.still_standing_frames == self.max_stillstanding_frames:
                self.initiate_reverse(dist_rear)
            else:
                self.still_standing_frames += 1
        else:
            self.still_standing_frames = 0

