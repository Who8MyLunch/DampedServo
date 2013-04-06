
import os
import time
import sys
import threading

import numpy as np
import scipy as sp
import scipy.stats

path_adafruit = '../Adafruit-Raspberry-Pi-Python-Code/Adafruit_PWM_Servo_Driver'
sys.path.append(os.path.abspath(path_adafruit))

import Adafruit_PWM_Servo_Driver

###############################################


class Response(object):
    """
    System response function.
    """
    def __init__(self, scale, y0=0):
        """
        Initialize with system time scale responsivity.
        Optionally initialize system value to a non-zero quantity.

        Assume an outside event loop is calling the output method fast enough
        that the internal state model is adequate.
        """
        self.scale = scale
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

        t_ref = sp.stats.norm.isf(0.01, self.scale)
        self.t1 = time.time() + t_ref


    def output(self):
        """
        Update state model and return output response.
        """
        t = time.time()
        dt = t - self.t1

        A = self.y1 - self.y0

        #if dt > 0:
        #    y = self.y0 + A*(1. - np.exp(-dt/self.tau))
        #else:
        #    y = self.y0

        frac = sp.stats.norm.cdf(dt, scale=self.scale)
        y = self.y0 + A*frac

        return dt, y

#################################################


class Servo(object):
    """
    Servo controller based on Adafruit support library for PWM board PCA9685.
    """

    def __init__(self, channel, info=None, vmin=None, vmax=None):
        """
        Create an instance of a servo controller.
        """

        if info:
            print('Configure servo: %s' % info['name'])
            vmin = info['vmin']
            vmax = info['vmax']
            sign = info['sign']

        # Default safe values.
        if not vmin:
            vmin = 200
        if not vmax:
            vmax = 450
        if not sign:
            sign = 1

        self.channel = channel
        self.period = 20. # milliseconds
        self.vmin = vmin
        self.vmax = vmax
        self.sign = sign

        self.pwm = Adafruit_PWM_Servo_Driver.PWM()

        freq = 1000. / self.period  # Hz
        self.pwm.setPWMFreq(freq)


    #@memoize
    def width_to_counts(self, width):
        """
        Convert pulse width from miliseconds to digital counts.
        For use with Adafruit servo library.
        """
        if not (0. <= width <= 1.0):
            raise ValueError('Invalid width: %s' % width)

        if self.sign < 0:
            width = 1. - width

        gain = (self.vmax - self.vmin)

        DN_start = 0
        DN_stop = self.vmin + width * gain

        DN_stop = int(np.round(DN_stop))

        # Done.
        return DN_start, DN_stop


    def pulse(self, width):
        """
        Send a pulse to the servo.
        width is a fractional value between 0 and 1.  It indicates the relative pulse width
        between the system minimum value and the system maximum value.
        """
        DN_start, DN_stop = self.width_to_counts(width)

        self.pwm.setPWM(self.channel, DN_start, DN_stop)

        # Done.
        return DN_start, DN_stop

###################################################


class DampedServo(Servo, threading.Thread):
    """
    Servo controller with first order response function.
    Controller lives in a background thread.
    """

    def __init__(self, channel, info, tau):
        """
        Create a new instance of a damped servo controller.
        """
        Servo.__init__(self, channel, info)
        threading.Thread.__init__(self)

        self.response = Response(tau, y0=0.5)
        self._tau = tau
        self.freq = 40.  # Hz.


    def __del__(self):
        print('DampedServo __del__')
        if self.isAlive():
            self.keep_running = False
            self.join()

    @property
    def tau(self):
        return self.response.tau

    @tau.setter
    def tau(self, value):
        self.response.tau = value
        
        
    def run(self):
        """
        This is where the work happens.
        """
        self.keep_running = True
        time_wait = 1./self.freq  
        while self.keep_running:
            #time_zero = time.time()

            dt, width = self.response.output()
            super(DampedServo, self).pulse(width)

            # Wait until end of time interval.
            #time_delta = time_wait - (time.time() - time_zero)
            #if time_delta > 0:
            #    time.sleep(time_delta)

            # Repeat loop.

        print('Servo exit: %d' % self.channel)

        # Done.


    def stop(self):
        if self.isAlive():
            self.keep_running = False
            print('Servo stopping: %d' % self.channel)


    def pulse(self, width):
        """
        Set new input value for servo.
        """
        self.response.force(width)
        
#################################################


info_sg92r  = {'name': 'SG-92r',  'vmin':125, 'vmax':540, 'sign':-1}
info_sg5010 = {'name': 'SG-5010', 'vmin':120, 'vmax':500, 'sign': 1}

if __name__ == '__main__':
    pass
    