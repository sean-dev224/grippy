import os
os.environ["BLINKA_FT232H"] = "1"
import time

#adafruit imports
import board
import busio
import digitalio
import adafruit_pca9685

#project files
from asyncServos import Servo
from asyncStepper import Stepper


i2c = board.I2C()
pca = adafruit_pca9685.PCA9685(i2c)
pca.frequency = 60

Servo.pca = pca

pitch_position_map = {
    0: 1900,
    30: 3150,
    60: 4520,
    90: 5900,
    120: 7350,
    150: 8560,
    180: 9740
}

roll_position_map = {
    0: 2100,
    90: 6100,
    180: 10000
}

gripper_position_map = {
    0: 5000,
    1: 6700
}

shoulder_position_map = {
    0: 2300,
    30: 3250,
    60: 4100,
    90: 5000,
    120: 5950,
    150: 6850,
    180: 7800,
    210: 8650,
    240: 9450,
    270: 10400
}

elbow_position_map = {
    0: 2350,
    30: 3200,
    60: 4050,
    90: 5000,
    120: 5900,
    150: 6900,
    180: 7750,
    210: 8600,
    240: 9500,
    270: 10500
}

shoulder = Servo(4, shoulder_position_map, shoulder_position_map[150])
elbow = Servo(5, elbow_position_map, elbow_position_map[150])
pitch = Servo(8, pitch_position_map, pitch_position_map[90])
roll = Servo(9, roll_position_map, roll_position_map[90])
gripper = Servo(10, gripper_position_map, gripper_position_map[0])

stepper = Stepper(board.C5, board.C4, 1.8 / 16, 0.0)


time.sleep(3)

def test_move():
    atPos = False
    while not atPos:
        atPos = Servo.update_position_all() and stepper.update_position()
        time.sleep(0.001)

stepper.assign_angle_move(0)
shoulder.assign_angle_move(45 + 180)
elbow.assign_angle_move(45 + 90)
pitch.assign_angle_move(90)
roll.assign_angle_move(90)
gripper.assign_angle_move(0)


test_move()
time.sleep(1)

stepper.assign_angle_move(110)
shoulder.assign_angle_move(45 + 135)
elbow.assign_angle_move(90)
gripper.assign_angle_move(1)

test_move()
time.sleep(1)

elbow.assign_angle_move(270)
shoulder.assign_angle_move(45 + 123)
gripper.assign_angle_move(0)
pitch.assign_angle_move(60)
roll.assign_angle_move(0)

test_move()
time.sleep(1)

stepper.assign_angle_move(90)

test_move()
time.sleep(1)

gripper.assign_angle_move(1)

test_move()
time.sleep(1)

stepper.assign_angle_move(0)
shoulder.assign_angle_move(45 + 100)
elbow.assign_angle_move(45 + 90)
pitch.assign_angle_move(90)
roll.assign_angle_move(90)


test_move()
time.sleep(1)

exit(0)





