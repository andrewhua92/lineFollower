from board import SCL, SDA
from adafruit_pca9685 import PCA9685
import busio
import time

# Initialization of the I2C communication on the current PWM chip (PCA9685)
i2c_bus = busio.I2C(SCL, SDA)

pca = PCA9685(i2c_bus)

pca.frequency = 60

# Sets values for the PCA9685 channels to send PWM signals from
motorLeft1A = pca.channels[0]
motorLeft1B = pca.channels[2]
enableLeft1 = pca.channels[1]

motorLeft2A = pca.channels[5]
motorLeft2B = pca.channels[3]
enableLeft2 = pca.channels[4]

motorRight1A = pca.channels[8]
motorRight1B = pca.channels[6]
enableRight1 = pca.channels[7]

motorRight2A = pca.channels[9]
motorRight2B = pca.channels[11]
enableRight2 = pca.channels[10]

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
        motorLeft1A.duty_cycle = lSpeed
        motorLeft1B.duty_cycle = 0
        enableLeft1.duty_cycle = 0xffff
        motorLeft2A.duty_cycle = lSpeed
        motorLeft2B.duty_cycle = 0
        enableLeft2.duty_cycle = 0xffff
    else:
        motorLeft1A.duty_cycle = 0
        motorLeft1B.duty_cycle = lSpeed * -1
        enableLeft1.duty_cycle = 0xffff
        motorLeft2A.duty_cycle = 0
        motorLeft2B.duty_cycle = lSpeed * -1
        enableLeft2.duty_cycle = 0xffff

    if rSpeed >= 0:
        motorRight1A.duty_cycle = rSpeed
        motorRight1B.duty_cycle = 0
        enableRight1.duty_cycle = 0xffff
        motorRight2A.duty_cycle = rSpeed
        motorRight2B.duty_cycle = 0
        enableRight2.duty_cycle = 0xffff
    else:
        motorRight1A.duty_cycle = 0
        motorRight1B.duty_cycle = rSpeed * -1
        enableRight1.duty_cycle = 0xffff
        motorRight2A.duty_cycle = 0
        motorRight2B.duty_cycle = rSpeed * -1
        enableRight2.duty_cycle = 0xffff

# Full stop function, halting all signals and disabling all enables
def stop():
    motorLeft1A.duty_cycle = 0
    motorLeft1B.duty_cycle = 0
    enableLeft1.duty_cycle = 0

    motorLeft2A.duty_cycle = 0
    motorLeft2B.duty_cycle = 0
    enableLeft2.duty_cycle = 0

    motorRight1A.duty_cycle = 0
    motorRight1B.duty_cycle = 0
    enableRight1.duty_cycle = 0

    motorRight2A.duty_cycle = 0
    motorRight2B.duty_cycle = 0
    enableRight2.duty_cycle = 0