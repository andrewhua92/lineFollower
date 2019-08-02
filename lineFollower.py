from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

# Variables for the resolution of the camera (640 x 480 px to enhance efficacy of OpenCV and FPS)
# Resolution is set rather low to increase processing speed
# May become an issue in detection if the complexity of program increases
xRes = 640
yRes = 480

# Lower and upper RGB values in arrays for convenience
# Brought to actual array forms using Numpy
lower = [0,0,0]
upper = [30, 30, 30]
lower = np.array(lower, dtype="uint8")
upper = np.array(upper, dtype="uint8")

# Initialization of the camera object to interact with it
camera = PiCamera()
camera.resolution = (xRes, yRes)
#camera.rotation = 180

# Integer value of the pixel value of the centre of the screen horizontally
centre = xRes/2

# Object to hold the camera feed
rawCapture = PiRGBArray(camera,size=(xRes,yRes))

# Intermittent delay to give camera time to boot
time.sleep(0.1)

# Endless loop until broken with the break key, which cycles through each frame of the camera feed
# In ours it will be 'r'
for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True ):
    # current image of the capture from camera
    image = frame.array

    # the region of interest
    # Y-coord, X-coord
    # the region is a strip along the middle to save computation time
    roi = image[int(yRes/2)-40:int(yRes/2)+40, 0:xRes]

    # a 'black and white' image of the current image
    blackSeen = cv2.inRange(image,lower, upper)

    # THIS SECTION IS TO DETERMINE LARGEST CONTOUR AREA AS A RESULT OF IMPROPERLY PLACED LINES / SYMBOLS
    ####################################################################################################
    # Creates a bitwise 'and' mask for what is black with the inRange function and in the original image
    bwResult = cv2.bitwise_and(image, image, mask=blackSeen)

    # Return the image and also the threshold
    ret, thresh = cv2.threshold(blackSeen, 40, 255, 0)
    # Applies contours to the new threshold
    img2, contour2, hi2 = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draws the contours onto the new 'bitwise-and' capture
    cv2.drawContours(bwResult, contour2, -1, 255, 3)

    # Creates a rectangle around the contour area with the largest area that is sees and prints it
    #
    largestContour = max(contour2, key = cv2.contourArea)
    xMax, yMax, wMax, hMax = cv2.boundingRect(largestContour)
    cv2.rectangle(bwResult, (xMax,yMax), (xMax+wMax,yMax+hMax), (0,255,0),3)
    ####################################################################################################

    # a 'green' image of the current image
    greenSeen = cv2.inRange(image, (0,50,0), (50,250,50))

    # a 'red' image of the current image
    redSeen = cv2.inRange(image, (0,0,50), (50,50,250))

    # creates a 3x3 matrix
    kernel = np.ones((3,3), np.uint8)

    # erodes 'cleans up' any noise and unreliable lines it sees
    # ideal number seems to be 3-7, will test later
    blackSeen= cv2.erode(blackSeen, kernel, iterations=5)
    greenSeen = cv2.erode(greenSeen, kernel, iterations=5)
    redSeen = cv2.erode(redSeen, kernel, iterations=5)

    # dilate 'ehances' the presently seen lines it sees
    # ideal number seems be 8-10, will test later
    blackSeen = cv2.dilate(blackSeen, kernel, iterations=9)
    greenSeen = cv2.dilate(greenSeen,kernel, iterations=9)
    redSeen = cv2.dilate(redSeen, kernel, iterations=9)

    # contour function
    # currently, this produces contours for anything seen that is very dark
    img, contour, hierarchy = cv2.findContours(blackSeen.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # draws out the contours that it finds
    #cv2.drawContours(blackSeen, contour, -1, (0,255,0), 3)

    # if there are any contours detected
    if len(contour) > 0:

        lineX,lineY,lineW,lineH = cv2.boundingRect(largestContour)
        lineCentre = (int)(lineX + (lineW/2))
        # camera is coloured in BGR
        cv2.line(image,(lineCentre, int(yRes/2)-40 ), (lineCentre,int(yRes/2)+40 ), (255,0,0), 3)
        cv2.rectangle(image, (lineX, lineY), (lineX+lineW, lineY+lineH), (255,0,0), 3)

        blackbox = cv2.minAreaRect(largestContour)
        (xMin, yMin), (wMin, hMin), ang = blackbox

        ang = int(ang)

        box = cv2.boxPoints(blackbox)
        box = np.int0(box)
        cv2.drawContours(image,[box], 0, (0,0,255,3))
        cv2.putText(image, str(ang), (10,40), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),2)

    # Calculation of the error
    # Also can be interpreted as distance of the line to the centre (or the colour it wishes to follow)
    error = lineCentre - centre
    message = "Distance from Centre :" + str(error)

    # Error Check code - will use the same information to move the rover
    cv2.putText(image, message, (10,250), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255,0,0), 2)

    # Display of the images

    cv2.imshow("Original", np.hstack([image,bwResult]))
    cv2.imshow("Black and White", blackSeen)
    cv2.imshow("Green", greenSeen)
    cv2.imshow("Red", redSeen)

    # Resets the buffer
    rawCapture.truncate(0)

    # Kill the process
    # Kill key is the letter 'r'
    key = cv2.waitKey(1) & 0xff
    if key == ord('r'):
        break

cv2.destroyAllWindows()
