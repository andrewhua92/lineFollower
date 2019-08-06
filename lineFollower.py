# Python program for a line-following rover using a Raspberry Pi and a CARobot Motor Hat
# Developed by Andrew Hua
# Credits go to the respective owners of the imported libaries and the OpenCV tutorials

# TO-DO:
# - Implement colour detection
# - Fix motion with rover
# - Implement contingencies for exception handling / errors

# The Pi required SSH, SPI, I2C, and the Camera functionality to be enabled

from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

import roverMovement as rm

# Variables for the resolution of the camera (640 x 480 px to enhance efficacy of OpenCV and FPS)
# Resolution is set rather low to increase processing speed
# May become an issue in detection if the complexity of program increases
xRes = 640
yRes = 480

# Lower and upper RGB values in arrays for convenience
# Brought to actual array forms using Numpy
lower = [0,0,0]
upper = [20, 20, 20]
lower = np.array(lower, dtype="uint8")
upper = np.array(upper, dtype="uint8")

# Values of the previous coordinates of x and y
xPrev = xRes/2
yPrev = yRes/2

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
    largestContour = max(contour2, key = cv2.contourArea)
    xMax, yMax, wMax, hMax = cv2.boundingRect(largestContour)

    #cv2.rectangle(bwResult, (xMax,yMax), (xMax+wMax,yMax+hMax), (0,255,0),3)
    ####################################################################################################

    # a 'green' image of the current image
    #greenSeen = cv2.inRange(image, (0,50,0), (50,250,50))

    # a 'red' image of the current image
    #redSeen = cv2.inRange(image, (0,0,50), (50,50,250))

    # creates a 3x3 matrix
    kernel = np.ones((3,3), np.uint8)

    # erodes 'cleans up' any noise and unreliable lines it sees
    # ideal number seems to be 3-7, will test later
    blackSeen= cv2.erode(blackSeen, kernel, iterations=5)
    #greenSeen = cv2.erode(greenSeen, kernel, iterations=5)
    #redSeen = cv2.erode(redSeen, kernel, iterations=5)

    # dilate 'ehances' the presently seen lines it sees
    # ideal number seems be 8-10, will test later
    blackSeen = cv2.dilate(blackSeen, kernel, iterations=9)
    #greenSeen = cv2.dilate(greenSeen,kernel, iterations=9)
    #redSeen = cv2.dilate(redSeen, kernel, iterations=9)

    # contour function
    # currently, this produces contours for anything seen that is very dark
    img, contour, hierarchy = cv2.findContours(blackSeen.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # draws out the contours that it finds
    cv2.drawContours(image, contour, -1, (0,255,255), 3)

    # Create variable for length of the number of contours
    contourLen = len(contour)
    # if there are any contours detected
    if contourLen > 0:

        # IF there are contours detected, then if only one is detected, simply use that for the smart box
        if contourLen == 1:
            smartBox = cv2.minAreaRect(contour[0])
        # check all false positives and find the most 'recent' based on change in x and y coordinates
        else:
            # Create empty array to hold all the candidate contours that appear in this frame
            allCntrs = []
            # Counter to see how many contours goes below the screen
            fromBottom = 0

            # Loop through all of the contours
            for i in range(contourLen):

                # Generate a rectangle of each contour, with the specifics of the lengths and angle
                smartBox = cv2.minAreaRect(contour[i])
                (xMin, yMin), (wMin, hMin), ang = smartBox

                # Store the coordinates of the rectangle
                box = cv2.boxPoints(smartBox)
                (xBox, yBox) = box[0]
                # If the y-coordinate of the lowest point is below the maximum screen size (480 pixels with room for
                # 2 pixels error), are NOT valid, which then it bumps the counter
                if yBox > yRes-2:
                    fromBottom+=1
                # Appends all of this into a list of information of the contours
                allCntrs.append((yBox,i,xMin,yMin))
            # Sorts the contours
            allCntrs = sorted(allCntrs)

            # If the number of false positives is
            if fromBottom > 1:
                # Create another array of contours from the bottom for distance
                cntrsFromBot = []

                # Loop through all of the contours that ARE valid (above the line lowest point of the screen)
                for i in range ((contourLen - fromBottom), contourLen):
                    # Set variables available from the initial contours variable
                    (yHighest, indexMax, xMin, yMin) = allCntrs[i]
                    # Calculate distance using the distance to a line formula
                    totalDistance = (abs(xMin - xPrev) ** 2 + abs(yMin - yPrev) ** 2) ** 0.5
                    # Append the index and also distance to the array
                    cntrsFromBot.append((totalDistance, indexMax))
                # Sort this array
                cntrsFromBot = sorted(cntrsFromBot)
                # Set variables for the indices and distances from the top of the array
                (totalDistance, indexMax) = cntrsFromBot[0]
                # The 'smart box' will now be created around the closest to last time's contour
                smartBox = cv2.minAreaRect(contour[indexMax])
            else:
                # If there is no off-bottom contours to disregard, simply choose the contour
                # at the bottom of the list (as we aim for lower yMax)
                (yMax, indexMax, xMin, yMin) = allCntrs[contourLen - 1]
                smartBox = cv2.minAreaRect(contour[indexMax])

        # DRAWING AND TEXT FOR RECENT CONTOUR
        # Set distance pairs from the smart box and also assign the previous values of the
        # x-coordinate and y-coordinate to the current values of the minimum
        (xMin, yMin), (wMin, hMin), ang = smartBox
        xPrev = xMin
        yPrev = yMin

        # Angle algorithm based on the orientation to see how much it takes to have
        # the 'box' to be flush with the center
        if ang < -45:
            ang = 90 + ang
        if wMin < hMin and ang > 0:
            ang = (90-ang) * -1
        if wMin > hMin and ang < 0:
            ang = 90 + ang
        ang = int(ang)

        # Prints the angle that it has with the center
        cv2.putText(image, str(ang), (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

        # Create a 'box' made from contours that would move with the direction and angle
        # of the line or object it is tracking
        recentBox = cv2.boxPoints(smartBox)
        recentBox = np.int0(recentBox)
        cv2.drawContours(image, [recentBox], 0, (255, 0, 255), 3)

        # Calculation of the error
        # Also can be interpreted as distance of the line to the centre (or the colour it wishes to follow)
        error = int(xMin - centre)
        message = "Distance from Centre (Recent) :" + str(error)

        # Error Check code - will use the same information to move the rover
        cv2.putText(image, message, (150, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        # Generate a line on the horizontal strip in the region of interest, as well as the rectangle that
        # represents the most recent contour found
        cv2.line(image, (int(xMin), 200), (int(xMin), 250), (255, 0, 255), 3)

        # DRAWING AND TEXT FOR LARGEST CONTOUR
        # Set distance pairs from the big box
        largestBox = cv2.minAreaRect(largestContour)
        (xBig, yBig), (wBig, hBig), angBig = largestBox

        # Angle algorithm based on the orientation to see how much it takes to have
        # the 'box' to be flush with the center
        if angBig < -45:
            angBig = 90 + angBig
        if wBig < hBig and angBig > 0:
            ang = (90-ang) * -1
        if wBig > hBig and angBig < 0:
            angBig = 90 + angBig
        angBig = int(angBig)

        # Prints the angle that is has with the center
        cv2.putText(image, str(angBig), (10,150), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,0),2)

        # Blue box and blue line signify the largest 'area' of contour detected
        # Generate the bounding rectangle of the largest contour found previously
        lineX, lineY, lineW, lineH = cv2.boundingRect(largestContour)
        lineCentre = (int)(lineX + (lineW / 2))

        # Generate a line on the horizontal strip in the region of interest, as well as the rectangle that
        # represents the largest contour found
        cv2.line(image, (lineCentre, int(yRes / 2) - 40), (lineCentre, int(yRes / 2) + 40), (255, 255, 0), 3)

        # Calculation of the error
        # Also can be interpreted as distance to the center (or the colour it wishes to follow)
        errorMax = int(lineCentre - centre)
        messageMax = "Distance from Centre (Biggest) :" + str(errorMax)

        # Error Check code - will use the same information to move the rover
        cv2.putText(image, messageMax, (150, 475), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,255), 2)

        # Create another 'box' made from contours that would move with the direction and angle
        # of the line or object it is tracking
        bigBox = cv2.boxPoints(largestBox)
        bigBox = np.int0(bigBox)
        cv2.drawContours(image, [bigBox], 0, (255, 255, 0), 3)

        if not errorMax is None:
            avgError = (errorMax + error)/2
        else:
            avgError = error
        if not angBig is None:
            avgAng = int((angBig + ang)/2)
        else:
            avgAng = ang

    # Display of the images
    cv2.imshow("Original", image)
    #cv2.imshow("Black and White", blackSeen)
    #cv2.imshow("Green", greenSeen)
    #cv2.imshow("Red", redSeen)

    # Resets the buffer
    rawCapture.truncate(0)

    # Kill the process
    # Kill key is the letter 'r'
    key = cv2.waitKey(1) & 0xff
    if key == ord('r'):
        break

# Kill the OpenCV windows
cv2.destroyAllWindows()
