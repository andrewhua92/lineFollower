from board import SCL, SDA
from adafruit_pca9685 import PCA9685
import busio
import time

# Initialization of the I2C communication on the current PWM chip (PCA9685)
i2c_bus = busio.I2C(SCL, SDA)

pca = PCA9685(i2c_bus)

pca.frequency = 60

# Sets values for the PCA9685 channels to send PWM signals from
motor1A = pca.channels[2]
motor1B = pca.channels[0]
enable1 = pca.channels[1]

motor2A = pca.channels[5]
motor2B = pca.channels[3]
enable2 = pca.channels[4]

# Movement functions
# Enable will detect a digital input, hence, why we use 0xffff as the signal to ensure a 'high' value
# Motor A and B are responsible for the speed at which the motors will run, ranging from 0 to 0xffff
# Movement will be using differential motion to turn or move towards a certain direction
# Left faster and forward & Right slower and forward / Right backwards turns left
# Left slower forward / Left backwards & Right faster and forward turns right
def move(leftSpeed, rightSpeed):
    # Map up the speeds to take values from 0 to 255 to ~0-0xffff
    lSpeed = int(leftSpeed*255)
    rSpeed = int(rightSpeed*255)

    if lSpeed >= 0:
        motor1A.duty_cycle = lSpeed
        motor1B.duty_cycle = 0
        enable1.duty_cycle = 0xffff
    else:
        motor1A.duty_cycle = 0
        motor1B.duty_cycle = lSpeed * -1
        enable1.duty_cycle = 0xffff

    if rSpeed >= 0:
        motor2A.duty_cycle = rSpeed
        motor2B.duty_cycle = 0
        enable2.duty_cycle = 0xffff
    else:
        motor2A.duty_cycle = 0
        motor2B.duty_cycle = rSpeed * -1
        enable2.duty_cycle = 0xffff

# Testing movement functions, where signal is at half duty-cycle
def leftMove(speed):
    lSpeed = int(speed * 255)
    if speed > 0:
        motor1A.duty_cycle = lSpeed
        motor1B.duty_cycle = 0
        enable1.duty_cycle = 0xffff
    elif speed < 0:
        motor1A.duty_cycle = 0
        motor1B.duty_cycle = lSpeed * -1
        enable1.duty_cycle = 0xffff
    else:
        motor1A.duty_cycle = 0
        motor1B.duty_cycle = 0
        enable1.duty_cycle = 0

def rightMove(speed):
    rSpeed = int(speed * 255)
    if speed > 0:
        motor2A.duty_cycle = rSpeed
        motor2B.duty_cycle = 0
        enable2.duty_cycle = 0xffff
    elif speed < 0:
        motor2A.duty_cycle = 0
        motor2B.duty_cycle = rSpeed * -1
        enable2.duty_cycle = 0xffff
    else:
        motor2A.duty_cycle = 0
        motor2B.duty_cycle = 0
        enable2.duty_cycle = 0

def forward():
    motor1A.duty_cycle = 0x7fff
    motor1B.duty_cycle = 0
    enable1.duty_cycle = 0xffff

    motor2A.duty_cycle = 0x7fff
    motor2B.duty_cycle = 0
    enable2.duty_cycle = 0xffff

def left():
    motor1A.duty_cycle = 0x7fff
    motor1B.duty_cycle = 0
    enable1.duty_cycle = 0xffff

    motor2A.duty_cycle = 0
    motor2B.duty_cycle = 0x7fff
    enable2.duty_cycle = 0xffff

def right():
    motor1A.duty_cycle = 0
    motor1B.duty_cycle = 0x7fff
    enable1.duty_cycle = 0xffff

    motor2A.duty_cycle = 0x7fff
    motor2B.duty_cycle = 0
    enable2.duty_cycle = 0xffff

def backwards():
    motor1A.duty_cycle = 0
    motor1B.duty_cycle = 0x7fff
    enable1.duty_cycle = 0xffff

    motor2A.duty_cycle = 0
    motor2B.duty_cycle = 0x7fff
    enable2.duty_cycle = 0xffff

# Full stop function, halting all signals and disabling all enables
def stop():
    motor1A.duty_cycle = 0
    motor1B.duty_cycle = 0
    enable1.duty_cycle = 0

    motor2A.duty_cycle = 0
    motor2B.duty_cycle = 0
    enable2.duty_cycle = 0