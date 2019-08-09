# Python program for a line-following rover using a Raspberry Pi and a CARobot Motor Hat
# Developed by Andrew Hua
# Credits go to the respective owners of the imported libaries and the OpenCV tutorials

# TO-DO:
# - Implement colour detection
# - Fix motion with rover
# - Implement contingencies for exception handling / errors
# - Handle crash of no contour found situation
# - Seperate images for separate masks?

# The Pi required SSH, SPI, I2C, and the Camera functionality to be enabled
# Currently using OpenCV version 3.4.4 - a bit outdated and will upgrade as soon as
# 4.00+ is available on PiWheels

from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

import roverMovement as rm

# Variables for the resolution of the camera (640 x 480 px to enhance efficacy of OpenCV and FPS)
# Resolution is set rather low to increase processing speed
# May become an issue in detection if the complexity of program increases
xRes = 350
yRes = 300

# Lower and upper BGR values in arrays for convenience
lowerBlack = (0,0,0)
upperBlack = (15, 15, 15)

lowerRed = (0,0,30)
upperRed = (40, 40, 255)

lowerGreen =(0, 30, 0)
upperGreen = (40, 255, 40)

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
    blackSeen = cv2.inRange(image,lowerBlack, upperBlack)

    # a 'green' image of the current image
    greenSeen = cv2.inRange(image, lowerGreen, upperGreen)

    # a 'red' image of the current image
    redSeen = cv2.inRange(image, lowerRed, upperRed)

    # creates a 3x3 matrix of 1's to reduce noise
    kernel = np.ones((3,3), np.uint8)

    # We want to 'open' the image' by eroding, then dilating to remove noise

    # erodes 'cleans up' any noise and unreliable lines it sees
    # ideal number seems to be 3-7, will test later
    blackSeen= cv2.erode(blackSeen, kernel, iterations=3)
    greenSeen = cv2.erode(greenSeen, kernel, iterations=3)
    redSeen = cv2.erode(redSeen, kernel, iterations=3)

    # dilate 'ehances' the presently seen lines it sees
    # ideal number seems be 8-10, will test later
    blackSeen = cv2.dilate(blackSeen, kernel, iterations=5)
    greenSeen = cv2.dilate(greenSeen,kernel, iterations=5)
    redSeen = cv2.dilate(redSeen, kernel, iterations=5)

    # contour function
    # produces contour arrays (made up of various point vectors) for corresponding colours
    _, contourBlack, hiBlack = cv2.findContours(blackSeen, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    _, contourGreen, hiGreen = cv2.findContours(greenSeen, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    _, contourRed, hiRed = cv2.findContours(redSeen, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Determines largest contour around dark regions, otherwise, tries again
    # This causes some issues, but this situation should typically not ever occur
    # as there should always be some region to check
    try:
        if len(contourBlack) > 0:
            largestBlkContour = max(contourBlack, key = cv2.contourArea)

        if len(contourRed) > 0:
            largestRedContour = max(contourRed, key = cv2.contourArea)

        if len(contourGreen) > 0:
            largestGrnContour = max(contourGreen, key = cv2.contourArea)
    except ValueError:
        rawCapture.truncate(0)
        continue

    # draws out the contours that it finds
    imageGreen = cv2.drawContours(image.copy(), contourGreen, -1, (0,255,255),3)
    imageRed = cv2.drawContours(image.copy(), contourRed, -1, (0,255,255),3)
    cv2.drawContours(image, contourBlack, -1, (0, 255, 255), 2)

    # Create variable for length of the number of contours
    contourLen = len(contourBlack)
    # If there are any contours detected...
    if contourLen > 0:

        # I there are contours detected, then if only one is detected, simply use that for the smart box
        if contourLen == 1:
            smartBox = cv2.minAreaRect(contourBlack[0])
        # Check all false positives and find the most 'recent' based on change in x and y coordinates
        else:
            # Create empty array to hold all the candidate contours that appear in this frame
            allCntrs = []
            # Counter to see how many contours goes below the screen
            fromBottom = 0

            # Loop through all of the contours
            for i in range(contourLen):

                # Generate a rectangle of each contour, with the specifics of the lengths and angle
                smartBox = cv2.minAreaRect(contourBlack[i])
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
                smartBox = cv2.minAreaRect(contourBlack[indexMax])
            else:
                # If there is no off-bottom contours to disregard, simply choose the contour
                # at the bottom of the list (as we aim for lower yMax)
                (yMax, indexMax, xMin, yMin) = allCntrs[contourLen - 1]
                smartBox = cv2.minAreaRect(contourBlack[indexMax])

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
        cv2.drawContours(image, [recentBox], 0, (255, 0, 255), 2)

        # Calculation of the error
        # Also can be interpreted as distance of the line to the centre (or the colour it wishes to follow)
        error = int(xMin - centre)
        message = "Distance from Centre (Recent) :" + str(error)

        # Error Check code - will use the same information to move the rover
        cv2.putText(image, message, (10, 290), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)

        # Generate a line on the horizontal strip in the region of interest, as well as the rectangle that
        # represents the most recent contour found
        cv2.line(image, (int(xMin), 200), (int(xMin), 250), (255, 0, 255), 3)

        # DRAWING AND TEXT FOR LARGEST CONTOUR
        # Set distance pairs from the big box
        largestBox = cv2.minAreaRect(largestBlkContour)
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
        lineX, lineY, lineW, lineH = cv2.boundingRect(largestBlkContour)
        lineCentre = (int)(lineX + (lineW / 2))

        # Generate a line on the horizontal strip in the region of interest, as well as the rectangle that
        # represents the largest contour found
        cv2.line(image, (lineCentre, int(yRes / 2) - 40), (lineCentre, int(yRes / 2) + 40), (255, 255, 0), 3)

        # Calculation of the error
        # Also can be interpreted as distance to the center (or the colour it wishes to follow)
        errorMax = int(lineCentre - centre)
        messageMax = "Distance from Centre (Biggest) :" + str(errorMax)

        # Error Check code - will use the same information to move the rover
        cv2.putText(image, messageMax, (10, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255, 0), 1)

        # Create another 'box' made from contours that would move with the direction and angle
        # of the line or object it is tracking
        bigBox = cv2.boxPoints(largestBox)
        bigBox = np.int0(bigBox)
        cv2.drawContours(image, [bigBox], 0, (255, 255, 0), 2)

        # Averaging of the distance to centre and averaging of error
        # This is assuming that a value has been procured from the 'big' contour as well as
        # an insignificant deviation between the two values
        # Priority is taken on the more recent contour as opposed to the big one

        # Positive value of error is distance from the right of the centre
        # Negative value of error is distance from the left of the centre
        if not errorMax is None and abs(errorMax - error) < 50:
            avgError = (errorMax + error)/2
        else:
            avgError = error

        # Positive value of angle is angle in degrees from the vertical from the centre to the right (quadrant 1)
        # Negative value of angle is angle in degrees from the vertical from the centre to the left (quadrant 2)
        if not angBig is None and abs(angBig - ang) < 50:
            avgAng = int((angBig + ang)/2)
        else:
            avgAng = ang

        # Based on the distance to the centre AND the angle it has perpindicular to the horizontal, it will move
        # the rover appropriately to correct itself - it wishes to have the line be dead-centre on the screen
        # motionMessage output purely for testing purposes
        if avgError > 0:
            # Move to the left
            if avgAng > 0:
                # Hard left
                rm.move(150, -100)
                motionMessage = 'hard left (on the right, angled right)'
            elif avgAng < 0:
                # Soft right
                rm.move(75,150)
                motionMessage = 'soft right (on the right, angled left)'
            else:
                # Soft left
                rm.move(150,75)
                motionMessage = 'soft left (on the right, angled correctly)'
        elif avgError < 0:
            # Move to the right
            if avgAng > 0:
                # Soft left
                rm.move(150,75)
                motionMessage = 'soft left (on the left, angled right)'
            elif avgAng < 0:
                # Hard right
                rm.move(-100,150)
                motionMessage = 'hard right (on the left, angled left)'
            else:
                # Soft right
                rm.move(75,150)
                motionMessage = 'soft right (on the left, angled correctly)'
        else:
            # Continue going straight
            if avgAng > 0:
                # Soft left
                rm.move(150,75)
                motionMessage = 'soft left (in the middle, angled right)'
            elif avgAng < 0:
                # Soft right
                rm.move(75,150)
                motionMessage = 'soft right (in the middle, angled left)'
            else:
                # Straight
                rm.move(150,150)
                motionMessage = 'straight (in the middle, angled correctly)'

        cv2.putText(image, 'Direction: '+ motionMessage, (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,255), 1)
                
    # Display of the images
    cv2.imshow("Original",image)
    cv2.imshow("Black and White", blackSeen)
    cv2.imshow("Green", imageGreen)
    cv2.imshow("Red", imageRed)

    # Resets the buffer
    rawCapture.truncate(0)

    # Kill the process & motor functio
    # Kill key is the letter 'r'
    key = cv2.waitKey(1) & 0xff
    if key == ord('r'):
        rm.stop()
        break

# Kill the OpenCV windows
cv2.destroyAllWindows()
