import os
os.environ["BLINKA_FT232H"] = "1"
import time
import sys

import board
import busio
import digitalio
import adafruit_pca9685

print(f"Board is {board.board_id}")


i2c = board.I2C()
pca = adafruit_pca9685.PCA9685(i2c)
pca.frequency = 60

#set up OE pin to stop servos
estop = digitalio.DigitalInOut(board.C0)
estop.direction = digitalio.Direction.OUTPUT
estop.value = False

#turn on led
led = digitalio.DigitalInOut(board.D7)
led.direction = digitalio.Direction.OUTPUT
led.value = True

class Servo():
    def __init__(self, channel: int, min_PWM: int, max_PWM: int, degree_range: int):
        self.channel = channel
        self.min_PWM = min_PWM
        self.max_PWM = max_PWM
        self.degree_range = degree_range

        self.duty_per_degree = (max_PWM - min_PWM) / degree_range
        self.current_position = min_PWM

    def move_to(self, pwm):
        pwm = int(pwm)

        #pwm limits
        if pwm > self.max_PWM:
            pwm = self.max_PWM
        elif pwm < self.min_PWM:
            pwm = self.min_PWM


        pca.channels[self.channel].duty_cycle = pwm
        self.current_position = pwm

        print(f"moved to {pwm}")

    def move_to_angle(self, angle):
        self.move_to(self.min_PWM + (angle * self.duty_per_degree))

    def move_to_angle_smooth(self, angle, travel_milliseconds):
        self.move_to_smooth(self.min_PWM + (angle * self.duty_per_degree), travel_milliseconds)

    def move_to_smooth(self, pwm, travel_milliseconds):
        pwm = int(pwm)
        distance = pwm - self.current_position
        pwm_per_ms = int(distance / travel_milliseconds)

        for i in range(self.current_position, pwm, pwm_per_ms):
            self.move_to(i)
            time.sleep(0.001)

        self.move_to(pwm)





def main():

    shoulder = Servo(9, 0, 0xFFFF, 360)

    servo_user_control(shoulder)

    elbow = Servo(5, 1650, 9750, 270)
    shoulder = Servo(4, 1800, 9900, 270)
    pitch = Servo(8, 1450, 9500, 180)
    roll = Servo(9, 2000, 9900, 180)
    gripper = Servo(10, 5000, 6700, 1)

    #start positions
    shoulder.move_to_angle(160)
    elbow.move_to_angle(220)
    pitch.move_to_angle(100)
    roll.move_to_angle(90)
    gripper.move_to_angle(0)
    time.sleep(2)

    shoulder.move_to_angle_smooth(178, 45)
    elbow.move_to_angle_smooth(250, 45)
    pitch.move_to_angle_smooth(80, 20)
    time.sleep(1)
    gripper.move_to_angle(1)
    time.sleep(2)

    shoulder.move_to_angle_smooth(160, 30)
    elbow.move_to_angle_smooth(90, 20)
    time.sleep(1)
    roll.move_to_angle_smooth(20, 20)
    time.sleep(1)
    roll.move_to_angle_smooth(160, 20)
    time.sleep(10)



    exit_handler()


def servo_user_control(servo: Servo):
    while True:
        position = int(input("Enter PWM: "))
        servo.move_to(position)

def servo_user_control_angle(servo: Servo):
    while True:
        position = int(input("Enter angle: "))
        servo.move_to_angle(position)

def servo_user_function(servo: Servo):
    while True:
        position = int(input("Enter angle: "))
        servo.move_to(1850 + (44.25 * position))

    

def servo_tune(servoChannel):
    print(f"Tuning Servo number {servoChannel}")
    servo = pca.channels[servoChannel]

    print("Running coarse tune")
    startRange = 0
    endRange = 0xFFFF
    increment = 0x0100
    
    for i in range(startRange, endRange, increment):
        servo.duty_cycle = i
        response = input(f"Pos: {i}  Enter y when it starts moving, n when it stops: ")
        if response == 'y':
            startRange = i - increment
        elif response == 'n':
            endRange = i
            break

    increment = 0x0040

    for i in range(startRange, endRange, increment):
        servo.duty_cycle = i
        response = input(f"Pos: {i}  Enter y when it starts moving, n when it stops: ")
        if response == 'y':
            startRange = i - increment
        elif response == 'n':
            endRange = i
            break

    print(f"Congrats. Start: {startRange}, End: {endRange}")


        

    


def exit_handler():
    print(" Exiting with ctrl-c")
    estop.value = True
    led.value = False


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit_handler()
        sys.exit(0)


