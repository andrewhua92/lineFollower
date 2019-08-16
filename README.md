# lineFollower
A Python project involving a Raspberry Pi, PiCamera, and the OpenCV libraries. A Work-In-progress.

# Description
Using a Raspberry Pi, PiCamera module, and a motor hat, the intention of the program will be able to see what is in front of it,
and move accordingly. The goal is for it to distinguish lines and follow them (black lines on a white surface, vice versa, and
hopefully a mix of colours). Additionally, it should be able to turn smoothly, stop appropriately upon seeing specific object
or colour cues (i.e. red to stop, yellow to reverse, etc). 

The algorithm will use two criteria to determine motion of the rover. The first is detecting the largest contour area that the 
rover will be able to detect. This will effectively have it search for the most likely 'line' or object to follow. Secondly,
it will use a recency bias search, where it will use previous x and y-coordinates of the previous frame from the camera feed to
determine which contour zone is the closest and establish that as the main contour to follow. Using the combination of these
methods will eliminate false-positive contours.

Motion is currently handled by two motors, using differential motion to turn. When using four motors, the ability for
the rover itself to turn is significantly reduced, hence, the decision to use two - this is not final however.

A state machine is being used in order for to move based on the current state of the line it sees from the camera, with
states of moving straight, turning left and right softly or sharply.

# Credits
Credits to the OpenCV developers and 'Out of the BOTS' on YouTube for the tutorials and the code to start off basic functionality.
Developed by Andrew Hua
