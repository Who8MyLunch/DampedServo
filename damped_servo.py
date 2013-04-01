
import os
import time
import sys

import numpy as np

path_adafruit = '../Adafruit-Raspberry-Pi-Python-Code/Adafruit_PWM_Servo_Driver'
sys.path.append(os.path.abspath(path_adafruit))

import Adafruit_PWM_Servo_Driver

#############################################


class memoize:
    """
    Copied from http://avinashv.net/2008/04/python-decorators-syntactic-sugar/
    """
    def __init__(self, function):
        self.function = function
        self.memoized = {}

    def __call__(self, *args):
        try:
            return self.memoized[args]
        except KeyError:
            self.memoized[args] = self.function(*args)
            return self.memoized[args]
        except TypeError:
            return self.function(*args)
            
###############################################


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
        self.y1 = y0
        self.t1 = 0 
        
        self.force(y0)        



    def force(self, y):
        """
        Set new system input value y.
        """
        dt0, y0 = self.output()
        self.y0 = y0
        
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

        return dt, y

        
        
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

    # Setup.
    tau = .5
    actions = [[0.,  0.],
               [1., 10.],
               [2.,  5.],
               [10, 0]]
    
    time_delta = 0.1
    
    # Do it.
    R = Response(tau)

    
    time_zero = time.time()
    time_action, y_action = actions.pop(0)
    
    while True:
        time_elapse = time.time() - time_zero

        if time_elapse >= time_action:
            # Apply new action.
            R.force(y_action)

            # Get next action ready to go.
            time_action, y_action = actions.pop(0)
            assert(time_action > time_elapse)
            
            
        # Clock tick.
        dt, y = R.output()

        print('%.3f, %.3f' % (time_elapse, y))
        
        # Pause and try again,
        time.sleep(time_delta)


    # Done.

        
        
        
        