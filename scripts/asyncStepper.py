import os
os.environ["BLINKA_FT232H"] = "1"
import time
import numpy as np

import digitalio


class Move():
    def __init__(self, start_angle: float, goal_angle: float, deg_per_s: float):
        self.start_time = time.monotonic_ns()
        self.start_angle = start_angle
        self.goal_angle = goal_angle
        self.deg_per_s = deg_per_s

        self.move_distance = abs(goal_angle - start_angle)
        self.move_time_ms = self.move_distance / (deg_per_s / 1000)

        self.CCW: bool #1 = clockwise
        if goal_angle - start_angle >= 0:
            self.CCW = True
        elif goal_angle - start_angle < 0:
            self.CCW = False
    
    def position_function(self) -> float:
        """
        returns: angle in degrees based on the time passed and the rate
        """
        elapsed_ms = (time.monotonic_ns() - self.start_time) / 1000000
        time_progress = elapsed_ms / self.move_time_ms

        #if stepper should to be at goal, return goal
        if elapsed_ms >= self.move_time_ms:
            return self.goal_angle

        move_progress = self.ease_in_out_cubic(time_progress)        

        desired_angle = np.interp(move_progress, [0, 1], [self.start_angle, self.goal_angle])

        return desired_angle

    
    def ease_in_out_sine(self, t):
        return -(np.cos(np.pi * t) - 1) / 2
    
    def ease_in_out_cubic(self, t):
        if t < 0.5:
            return 4 * t**3
        else:
            return 1 - (-2 * t + 2)**3 / 2
        

class Stepper():
    def __init__(self, step_pin: int, direction_pin: int, step_angle: float, start_angle = 0):
        self.step_pin = digitalio.DigitalInOut(step_pin)
        self.step_pin.direction = digitalio.Direction.OUTPUT

        self.direction_pin = digitalio.DigitalInOut(direction_pin)
        self.direction_pin.direction = digitalio.Direction.OUTPUT

        self.step_angle = step_angle
        self.current_angle = start_angle

        self.move: Move

    def step(self):
        self.step_pin.value = True
        time.sleep(0.000001)
        self.step_pin.value = False
        time.sleep(0.000001)

        if self.direction_pin.value == True:
            self.current_angle += self.step_angle
        else:
            self.current_angle -= self.step_angle

        print(f"Stepped to {self.current_angle}")

    def set_direction(self, CCW: bool):
        """
        Sets step pin direction
        Rotation direction is with shaft pointing towards you

        :param CCW: Motor rotates counter-clockwise if True, clockwise if False
        """
        self.direction_pin.value = CCW

    def assign_angle_move(self, goal_angle: float, deg_per_s: float = 20.0):
        """
        Creates a new move object and assigns it to the servo

        :param goal_angle: the desired angle in degrees
        :param rate: pwm change per ms - a rough measure for speed
        """

        self.move = Move(self.current_angle, goal_angle, deg_per_s)
        self.set_direction(self.move.CCW)

    def update_position(self) -> bool:
        """
        Non-blocking position update intended to be call many times per second

        :return bool: True if motor is at goal position, False otherwise
        """
        #if stepper is less than one step away from the goal
        if abs(self.current_angle - self.move.goal_angle) <= self.step_angle:
            return True
        
        desired_angle = self.move.position_function()

        if abs(self.current_angle - desired_angle) > self.step_angle:
            self.step()

        

    