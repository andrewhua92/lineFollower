import roverMovement as rm

# class to handle transition of states - can be see as a Mealy SM
class stateMachine:

    # states are as defined as the motion of the rover, based on the angle it
    # presents to the vertical in the centre, and the distance (horizontally)
    # to the centre
    # start state is the straight motion
    states = ['straight', 'softRight','hardRight'
              'softLeft', 'hardLeft']
    startState = states[0]
    currState = startState

    # dictionary for the states and their associated motions
    roverMotion =  {'straight': rm.move(50,50),
                    'softRight': rm.move(30,50),
                    'hardRight': rm.move(-30,50),
                    'softLeft': rm.move(50,30),
                    'hardLeft': rm.move(50,-30)
    }

    # extremely bruteforce transition for the current angle, distance and state
    # so it should be only able to turn and change states with non-drastic
    # change in state of motion
    # currently thinking of a better way to do this
    # FORMAT:
    # ('angle', 'orientation', 'previousState') : 'nextState'
    transition = {('firstQuad', 'right', 'softLeft'): 'hardLeft',
                  ('firstQuad', 'left', 'straight'): 'softLeft',
                  ('firstQuad', 'left', 'hardLeft'): 'softLeft',
                  ('firstQuad', 'vertical', 'straight'):'softLeft',
                  ('firstQuad', 'vertical', 'hardLeft'): 'softLeft',
                  ('secondQuad', 'right', 'straight'): 'softRight',
                  ('secondQuad', 'right', 'hardRight'): 'softRight',
                  ('secondQuad', 'left', 'softRight'): 'hardRight',
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
        ang = self.angleHelper(angle)
        dist = self.distanceHelper(distance)
        try:
            self.currState = self.transition[(ang,dist,self.currState)]
            self.roverMotion[self.currState]()
        finally:
            return ang + " and " + dist + " ; " + self.currState

    # angle definition function to determine what type of angular situation it is
    def angleHelper(self, angle):
        # definitions based on Cartesian location with respect to y-axis in the centre
        if angle > 0:
            return 'firstQuad'
        elif angle < 0:
            return 'secondQuad'
        else:
            return 'vertical'

    # distance definition function to determine what type of distance situation it is
    def distanceHelper(self, distance):
        # definitions based on location of either left or right with respect to y-axis in the centre
        if distance > 0:
            return 'right'
        elif distance < 0:
            return 'left'
        else:
            return 'vertical'