
import os
import time

import numpy as np


path_adafruit = 'Adafruit-Raspberry-Pi-Python-Code/Adafruit_PWM_Servo_Driver'
sys.path.append(os.path.abspath(path_adafruit))

import Adafruit_PWM_Servo_Driver

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

    def __init__(self, channel=None, p_min=1., p_zero=1.5, p_max=2.0):
        """
        Create an instance of a damnped servo controller.
        Playing with something here.
        """
        period = 20.
        
        self.channel = channel
        self.period = period
        self.p_min = p_min
        self.p_zero = p_zero
        self.p_max = p_max




if __name__ == '__main__':
    """
    My little example.
    """
    channel = 5
    
