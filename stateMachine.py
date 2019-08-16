import roverMovement as rm

# class to handle transition of states - can be see as a Mealy SM
class stateMachine:

    # states are as defined as the motion of the rover, based on the angle it
    # presents to the vertical in the centre, and the distance (horizontally)
    # to the centre - this array doesn't really get used much at the moment
    # start state is the straight motion
    states = ['straight', 'softRight','hardRight'
              'softLeft', 'hardLeft']
    startState = states[0]
    currState = startState

    # dictionary for the states and their associated motions
    # speeds are to be tested
    roverMotion =  {'straight': (rm.move, (50,50)),
                    'softRight': (rm.move, (50,30)),
                    'hardRight': (rm.move, (30,-30)),
                    'softLeft': (rm.move, (30,50)),
                    'hardLeft': (rm.move, (-30, 30))
    }

    # Extremely bruteforce transition for the current angle, distance and state
    # so it should be only able to turn and change states with non-drastic
    # change in state of motion - self-looping states are NOT considered,
    # instead those are handled in a try-catch block

    # Distance takes precedence over angle
    # currently thinking of a better way to do this
    # FORMAT:
    # ('angle', 'orientation', 'previousState') : 'nextState'
    transition = {('firstQuad', 'right', 'softRight'): 'hardRight',
                  ('firstQuad', 'right', 'straight'): 'softRight',
                  ('firstQuad', 'left', 'straight'): 'softLeft',
                  ('firstQuad', 'left', 'hardLeft'): 'softLeft',
                  ('firstQuad', 'vertical', 'straight'):'softRight',
                  ('firstQuad', 'vertical', 'hardRight'): 'softRight',
                  
                  ('secondQuad', 'right', 'straight'): 'softRight',
                  ('secondQuad', 'right', 'hardRight'): 'softRight',
                  ('secondQuad', 'left', 'softRight'): 'hardRight',
                  ('secondQuad', 'left', ''): '',
                  ('secondQuad', 'vertical', 'straight'): 'softRight',
                  ('secondQuad', 'vertical', 'hardRight'): 'softRight',
                  
                  ('vertical', 'right', 'straight'): 'softLeft',
                  ('vertical', 'right', 'hardLeft'): 'softLeft',
                  ('vertical', 'left', 'straight'): 'softRight',
                  ('vertical', 'left', 'hardRight'): 'softRight',
                  ('vertical', 'vertical', 'softRight'): 'straight',
                  ('vertical', 'vertical', 'softLeft'): 'straight'
    }

    # main function used to take in current angle and distance to centre
    # returns the direction and situation for debugging while code runs
    def drive(self, angle, distance):

        # stores the status of the presently seen angle and distance
        ang = self.angleHelper(angle)
        dist = self.distanceHelper(distance)

        # try-catch block to try and move states (essentially motions from hard left to hard right)
        try:
            self.currState = self.transition[(ang,dist,self.currState)]
        except:
            # debugging code
            print("old state :", self.currState, " - rover motion : ", self.roverMotion[self.currState][1])
        else:
            # debugging code
            print("new state :", self.currState, " - rover motion : ", self.roverMotion[self.currState][1])
        finally:
            # call the method (stored in the first element of the value)
            # pass the parameters stored in the 2nd value of the value array
            self.roverMotion[self.currState][0](self.roverMotion[self.currState][1][0],
                                                self.roverMotion[self.currState][1][1])

            # returns a status message of the current angle, distance, and state
            return ang + " and " + dist + " ; " + self.currState

    # angle definition function to determine what type of angular situation it is
    def angleHelper(self, angle):
        # definitions based on Cartesian location with respect to y-axis in the centre
        # loose values used to allow marginal error
        if angle > 5:
            return 'firstQuad'
        elif angle < -5:
            return 'secondQuad'
        else:
            return 'vertical'

    # distance definition function to determine what type of distance situation it is
    def distanceHelper(self, distance):
        # definitions based on location of either left or right with respect to y-axis in the centre
        # loose values used to allow marginal error
        if distance > 10:
            return 'right'
        elif distance < -10:
            return 'left'
        else:
            return 'vertical'