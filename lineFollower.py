from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
#import RPi.GPIO as GPIO

#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(40, GPIO.OUT)
#GPIO.output(40, GPIO.HIGH)

#GPIO.setwarnings(False)

# Resolution is set rather low to increase processing speed
# May become an issue in detection if the complexity of program increases
camera = PiCamera()
camera.resolution = (300, 300)
#camera.rotation = 180
centre = 150
rawCapture = PiRGBArray(camera,size=(300,300))

time.sleep(0.1)

for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True ):
    # current image of the capture from cmaera
    image = frame.array

    # Y-coord, X-coord
    roi = image[125:175, 0:300]
    # a 'black and white' image of the current image
    blackSeen = cv2.inRange(roi,(0,0,0), (50,50,50))

    # a 'green' image of the current image
    greenSeen = cv2.inRange(image, (0,50,0), (100,250,100))

    # a 'red' image of the current image
    redSeen = cv2.inRange(image, (0,0,50), (100,100,250))

    # creates a 3x3 matrix
    kernel = np.ones((3,3), np.uint8)

    # erodes 'cleans up' any noise and unreliable lines it sees
    blackSeen= cv2.erode(blackSeen, kernel, iterations=5)
    greenSeen = cv2.erode(greenSeen, kernel, iterations=5)
    redSeen = cv2.erode(redSeen, kernel, iterations=5)

    # dilate 'ehances' the presently seen lines it sees
    blackSeen = cv2.dilate(blackSeen, kernel, iterations=9)
    greenSeen = cv2.dilate(greenSeen,kernel, iterations=9)
    redSeen = cv2.dilate(redSeen, kernel, iterations=9)

    # contour function
    img, contour, hierarchy = cv2.findContours(blackSeen.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cv2.drawContours(image, contour, -1, (0,255,0), 3)
    #cv2.imshow("Black inRange", blackLine)

    if len(contour) > 0:

        lineX,lineY,lineW,lineH = cv2.boundingRect(contour[0])
        lineCentre = (int)(lineX + (lineW/2))
        # camera is coloured in BGR
        cv2.line(image,(lineCentre, 125), (lineCentre, 175), (255,0,0), 3)

    error = lineCentre - centre
    message = "Distance from Centre :" + str(error)

    # Error Check code - will use the same information to move the rover
    cv2.putText(image, message, (10,250), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255,0,0), 2)

    # Display of code
    cv2.imshow("Original", image)
    cv2.imshow("Green", greenSeen)
    cv2.imshow("Red", redSeen)

    rawCapture.truncate(0)
    key = cv2.waitKey(1) & 0xff
    if key == ord('q'):
        break

# Code for colour-space differentiation
'''
for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
    image = frame.array

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lowerRed = np.array([30,50,175])
    upperRed = np.array([150,150,250])

    mask = cv2.inRange(hsv, lowerRed, upperRed)

    res = cv2.bitwise_and(image, image, mask=mask)

    cv2.imshow('Frame', image)
    cv2.imshow('Mask', mask)
    cv2.imshow('Res', res)

    rawCapture.truncate(0)

    k = cv2.waitKey(5) & 0XFF
    if k == 27:
        break
'''
cv2.destroyAllWindows()



#GPIO.output(40, GPIO.LOW)