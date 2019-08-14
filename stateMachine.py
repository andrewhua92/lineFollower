import roverMovement as rm

class stateMachine:

    startState = 'straight'
    currState = startState
    states = ['straight', 'softRight','hardRight'
              'softLeft', 'hardLeft']

    roverCalls = {'straight': rm.move(50,50),
                 'softRight': rm.move(50,75),
                 'hardRight': rm.move(-20,50),
                 'softLeft': rm.move(75,50),
                 'hardLeft': rm.move(50,-20)
    }

    transition = {('firstQuad', 'right'): 'hardLeft',
                  ('firstQuad', 'left'): 'softLeft',
                  ('firstQuad', 'vertical'):'softLeft',
                  ('secondQuad', 'right'): 'softRight',
                  ('secondQuad', 'left'): 'hardRight',
                  ('secondQuad', 'vertical'): 'softRight',
                  ('vertical', 'right'): 'softLeft',
                  ('vertical', 'left'): 'softRight',
                  ('vertical', 'vertical'): 'straight'
    }
    
    def drive(self, angle, distance):
        ang = self.angleHelper(angle)
        dist = self.distanceHelper(distance)
        
        direction = self.transition[(ang,dist)]
        self.roverCalls = [direction]
        return ang + " and " + dist + " ; " + direction

    def angleHelper(self, angle):
        if angle > 0:
            return 'firstQuad'
        elif angle < 0:
            return 'secondQuad'
        else:
            return 'vertical'

    def distanceHelper(self, distance):
        if distance > 0:
            return 'right'
        elif distance < 0:
            return 'left'
        else:
            return 'vertical'