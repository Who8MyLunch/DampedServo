
import os
import time

import numpy as np

class Response(object):
    """
    System response function.
    """
    def __init__(self, tau, y0=0):
        """
        Initialize with system time constant.
        Optionally initialize system value to a non-zero quantity.
        """
        self.tau = tau
        self.y0 = y0
        self.y1 = y0
        self.t1 = 0


    def input(self, y1, t1=None):
        """
        Define system input y1 to system at time t1.
        """
        if not t1:
            t1 = time.time()
            
        self.y1 = y1
        self.t1 = t1



    def output(self, t=None):
        """
        Return system response at time t.
        """
        if not t:
            t = time.time()
            
        A = self.y1 - self.y0
        dt = t - self.t1
        
        if dt > 0:
            y = self.y0 + A*(1. - np.exp(-dt/self.tau))
        else:
            y = self.y0

        return y

    

class Servo(object):
    """
    Damped servo controller.
    """

    def __init__(self, p_min=1., p_zero=1.5, p_max=2.0):
        """
        Create an instance of a damnped servo controller.
        Playing with something here.
        """
        self.channel = channel
        self.p_min = p_min
        self.p_zero = p_zero
        self.p_max = p_max

    def set_target(self, target):
        """
        Set new value for servo target position.
        """
        pass

    def __iter__(self):
        """
        Iterator yielding current output
        """
        pass



def my_gen(info):
    """
    My little generator.
    """

    count = 0
    while info['flag']:
        count += 2
        yield count




if __name__ == '__main__':

    info = {'flag': True}

    G = my_gen(info)

    c = 0
    for v in G:
        c += 1
        print(v)

        if c > 5:
            info['flag'] = False
