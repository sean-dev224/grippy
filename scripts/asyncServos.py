import time
import numpy as np

import adafruit_pca9685


class Move():
    def __init__(self, start_pwm: int, goal_pwm: int, rate: int):
        self.start_time = time.perf_counter_ns()
        self.start_pwm = start_pwm
        self.goal_pwm = goal_pwm
        self.rate = rate

        self.move_distance = abs(goal_pwm - start_pwm)
        self.move_time = self.move_distance / rate

        self.direction: int
        if start_pwm < goal_pwm:
            self.direction = 1
        elif start_pwm > goal_pwm:
            self.direction = -1
        else:
            self.direction = 0
    
    def position_function(self) -> int:
        """
        returns: pwm based on the time passed and the rate
        """
        elapsed_ms = (time.perf_counter_ns() - self.start_time) / 1000000
        time_progress = elapsed_ms / self.move_time

        #if servo should to be close to goal, just go to goal
        if elapsed_ms >= self.move_time:
            return self.goal_pwm

        move_progress = self.ease_in_out_cubic(time_progress)        

        desired_pwm = np.interp(move_progress, [0, 1], [self.start_pwm, self.goal_pwm])

        return int(desired_pwm)

    
    def ease_in_out_sine(self, t):
        return -(np.cos(np.pi * t) - 1) / 2
    
    def ease_in_out_cubic(self, t):
        if t < 0.5:
            return 4 * t**3
        else:
            return 1 - (-2 * t + 2)**3 / 2

         

class Servo():
    pca: adafruit_pca9685.PCA9685 = None
    all_servos = []

    def __init__(self, channel: int, position_map: dict[int: int], safe_position: int):
        if Servo.pca == None:
            raise ValueError("Assign PCA to the Servo class before using!")
        
        self.channel = channel

        position_list = sorted(position_map.items())
        self.min_pwm = position_list[0][1]
        self.max_pwm = position_list[-1][1]
        self.safe_position = safe_position
        self.position_map = dict(position_list)

        self.current_pwm: int
        self.move: Move


        Servo.all_servos.append(self)

        #move to a known position during startup
        self.set_pwm(safe_position)


    def set_pwm(self, pwm):
        """
        Sets the duty cycle of the servo and updates current_pwm
        Clamps values to the range described by min_pwm and max_pwm

        :param pwm: the duty cycle pwm value
        :return: None
        """
        pwm = int(pwm)

        #pwm limits
        if pwm > self.max_pwm:
            pwm = self.max_pwm
        elif pwm < self.min_pwm:
            pwm = self.min_pwm

        Servo.pca.channels[self.channel].duty_cycle = pwm
        self.current_pwm = pwm

        print(f"Moved to {pwm}")

    def assign_pwm_move(self, goal_pwm: int, rate: int = 2):
        """
        Creates a new move object and assigns it to the servo

        :param goal_pwm: the desired pwm value
        :param rate: pwm change per ms - a rough measure for speed
        """
        move = Move(self.current_pwm, goal_pwm, rate)
        move.start_pwm = self.current_pwm

        self.move = move

    def assign_angle_move(self, goal_angle, rate: int = 2):
        """
        Creates a new move object and assigns it to the servo

        :param goal_angle: the desired angle in degrees
        :param rate: pwm change per ms - a rough measure for speed
        """

        self.assign_pwm_move(self.degrees_to_pwm(goal_angle), rate)


    def degrees_to_pwm(self, desired_angle) -> int:
        """
        Converts an angle in degrees to a pwm value
        using the Servo object's position map

        :param desired_angle: angle in degrees
        :return: a pwm value
        """
        angles = list(self.position_map.keys())
        pwm_values = list(self.position_map.values())

        if desired_angle < angles[0] or desired_angle > angles[-1]:
            raise ValueError(f"Angle {desired_angle} out of range {angles[0]}-{angles[-1]} degrees")
        
        return int(np.interp(desired_angle, angles, pwm_values))     


    def update_position(self) -> bool:
        """
        Non-blocking servo position update intended to be call many times per second

        :return bool: True if servo is at goal position, False otherwise
        """
        if self.move == None:
            return True
        
        if abs(self.current_pwm - self.move.goal_pwm) == 0:
            return True
        
        desired_pwm = self.move.position_function()

        self.set_pwm(desired_pwm)

    @classmethod
    def update_position_all(cls) -> bool:
        """
        Non-blocking servo position update intended to be call many times per second
        Acts on all servos

        :return bool: True if all servos are at their goal position, False otherwise
        """
        result = True
        for servo in cls.all_servos:
            result = servo.update_position() and result

        return result
    
    @classmethod
    def assign_all_safe(cls):
        for servo in cls.all_servos:
            servo.assign_pwm_move(servo.safe_position, 1)



        