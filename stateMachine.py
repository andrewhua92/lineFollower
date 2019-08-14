import roverMovement as rm

class stateMachine:

    states = ['straight', 'softRight','hardRight'
              'softLeft', 'hardLeft']
    startState = states[0]
    currState = startState

    roverCalls = {'straight': rm.move(50,50),
                 'softRight': rm.move(50,75),
                 'hardRight': rm.move(-20,50),
                 'softLeft': rm.move(75,50),
                 'hardLeft': rm.move(50,-20)
    }

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
    
    def drive(self, angle, distance):
        ang = self.angleHelper(angle)
        dist = self.distanceHelper(distance)
        try:
            self.currState = self.transition[(ang,dist,self.currState)]
        finally:
            return ang + " and " + dist + " ; " + self.currState

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