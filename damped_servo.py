
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
    def __init__(self, scale, y_set=0.):
        """
        Initialize with system time scale responsivity.
        Optionally initialize system value to a non-zero quantity.

        Assume an outside event loop is calling the output method fast enough
        that the internal state model is adequate.
        """
        self.scale = scale

        self.t_set = time.time()
        self.y_set = y_set
        self.y_ref = y_set
        self.y_now = y_set

        
    def force(self, y):
        """
        Set new system input value y.
        """
        self.y_ref = self.output()
        self.y_set = y
        
        self.t_set = time.time()
        

    def output(self, t=None):
        """
        Update state model and return output response.
        """
        
        # Use supplied time?
        if not t:
            t = time.time()
            
        dt = t - self.t_set
        frac = 1. - np.exp(-dt/self.scale)        

        y = self.y_ref + (self.y_set - self.y_ref)*frac
        self.y_now = y
        
        # Done.
        return y

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
        self.period = 20.# milliseconds
        self.vmin = vmin
        self.vmax = vmax
        self.sign = sign

        self.start_stop = (0, 0)
        
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

        if not self.start_stop == (DN_start, DN_stop):
            self.start_stop = (DN_start, DN_stop)
            self.pwm.setPWM(self.channel, DN_start, DN_stop)

        # Done.
        return DN_start, DN_stop

###################################################


class DampedServo(Servo, threading.Thread):
    """
    Servo controller with first order response function.
    Controller lives in a background thread.
    """

    def __init__(self, channel, info, scale, limiter=None):
        """
        Create a new instance of a damped servo controller.
        """
        Servo.__init__(self, channel, info)
        threading.Thread.__init__(self)

        self.response = Response(scale)
        self.freq = 70.  # Hz.
        self.alpha = 0.05
        
        self.lock = threading.Lock()


    def __del__(self):
        """
        Cleanup when this object is deleted.
        """
        if self.isAlive():
            print('DampedServo __del__')
            self.keep_running = False
            self.join()

            
    @property
    def scale(self):
        return self.response.scale

        
    @scale.setter
    def scale(self, value):
        self.response.scale = value
        
    
    def run(self):
        """
        This is where the work happens.
        """
        self.keep_running = True
        time_wait = 1./self.freq

        time_A = time.time()
        cnt = 0
        width = self.response.output()
        while self.keep_running:

            cnt += 1
            self.lock.acquire()
            width_old = width
            width_new = self.response.output()
            width = self.alpha * width_new + (1. - self.alpha) * width_old

            #if self.limiter:
            #    width = self.limiter(width)
                
            if 0 <= width <= 1.:
                super(DampedServo, self).pulse(width)
            else:
                print('warning, invalid width: %.1f' % (width))

            self.lock.release()
            time.sleep(time_wait)
            

        # Loop finished.
        time_B = time.time()
        dt = time_B - time_A
        freq = cnt / dt

        print('Servo run loop exit: %d [%.1f Hz]' % (self.channel, freq))

        # Done.


    def stop(self):
        if self.isAlive():
            self.keep_running = False
            print('Servo stopping: %d' % self.channel)


    def pulse(self, width):
        """
        Set new input value for servo.
        """
        self.lock.acquire()
        self.response.force(width)
        self.lock.release()
        
#################################################


info_sg92r  = {'name': 'SG-92r',  'vmin':125, 'vmax':540, 'sign':-1, 'scale':None}
info_sg5010 = {'name': 'SG-5010', 'vmin':120, 'vmax':500, 'sign': 1, 'scale':None}

if __name__ == '__main__':
    pass
    
