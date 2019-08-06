from board import SCL, SDA
from adafruit_pca9685 import PCA9685
import busio
import time

i2c_bus = busio.I2C(SCL, SDA)

pca = PCA9685(i2c_bus)

pca.frequency = 60

motor1A = pca.channels[0]
motor1B = pca.channels[2]
enable1 = pca.channels[1]

motor2A = pca.channels[3]
motor2B = pca.channels[5]
enable2 = pca.channels[4]

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

def stop():
    motor1A.duty_cycle = 0
    motor1B.duty_cycle = 0
    enable1.duty_cycle = 0

    motor2A.duty_cycle = 0
    motor2B.duty_cycle = 0
    enable2.duty_cycle = 0