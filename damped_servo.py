
import os
import time
import sys

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
        
        Assume an outside event loop is calling the output method fast enough
        that the internal state model is adequate.
        """
        self.tau = tau
        self.y0 = y0 
        
        self.force(y0)        



    def force(self, y):
        """
        Set new system input value y.
        """
        self.y0 = self.output()
        
        self.y1 = y
        self.t1 = time.time()



    def output(self):
        """
        Update state model and return system response at current time.
        """
        t = time.time()
        dt = t - self.t1
        
        A = self.y1 - self.y0
        
        if dt > 0:
            y = self.y0 + A*(1. - np.exp(-dt/self.tau))
        else:
            y = self.y0

        return y

        
        
class Servo(object):
    """
    Damped servo controller based on Adafruit PCA9685.
    """

    def __init__(self, channel=None, p_min=1., p_zero=1.5, p_max=2.0):
        """
        Create an instance of a damnped servo controller.
        Playing with something here.
        """
        period = 20.
        
        self.channel = channel
        self.p_min = p_min
        self.p_zero = p_zero
        self.p_max = p_max
        self.period = period

        self.pwm = Adafruit_PWM_Servo_Driver.PWM()
        freq = 1000. / self.period
        self.pwm.setPWMFreq(freq)


    @memoize
    def start_stop(self, period, width):
        """
        period and width in milliseconds.
        """
        DN_min = 0.
        DN_max = 2.**12

        # counts per millisecond
        gain = (DN_max - DN_min) / period

        start = 0
        stop = start + width * gain

        stop = int(np.round(stop))

        # Done.
        return start, stop


        
    def pulse(self, width):
        """
        Send a pulse of specified width to the servo.
        width: pulse width in milliseconds.
        """
        start, stop = start_stop(self.period, width)
        
        self.pwm.setPWM(self.channel, start, stop)
        
        # Done.
        

if __name__ == '__main__':
    """
    My little example.
    """
    channel = 5
    
