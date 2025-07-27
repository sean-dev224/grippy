import os
os.environ["BLINKA_FT232H"] = "1"
import time

import board
import digitalio

from asyncStepper import Stepper, Move

i2c = board.I2C()

stepper = Stepper(board.C5, board.C4, 1.8 / 16, 0.0)

def test_move():
    atPos = False
    while not atPos:
        atPos = stepper.update_position()
        time.sleep(0.001)

time.sleep(1)

stepper.assign_angle_move(90)
test_move()

time.sleep(1)

stepper.assign_angle_move(0)
test_move()


# step_pin = digitalio.DigitalInOut(board.C5)
# step_pin.direction = digitalio.Direction.OUTPUT
# direction_pin = digitalio.DigitalInOut(board.C4)
# direction_pin.direction = digitalio.Direction.OUTPUT

# def step():
#         step_pin.value = True
#         time.sleep(0.0001)
#         step_pin.value = False
#         time.sleep(0.0001)

# while True:
#     step()
#     print("Step!")
#     time.sleep(0.5)



