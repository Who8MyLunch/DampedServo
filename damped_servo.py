
import os
import time
import sys
import threading

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
        Update state model and return output response.
        """
        t = time.time()
        dt = t - self.t1

        A = self.y1 - self.y0

        if dt > 0:
            y = self.y0 + A*(1. - np.exp(-dt/self.tau))
        else:
            y = self.y0

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


    @memoize
    def width_to_counts(self, width):
        """
        Convert pulse width from miliseconds to digital counts.
        For use with Adafruit servo library.
        """
        assert(0. <= width <= 1.0)

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

        self.response = Response(tau, y0=info['vmin'])
        self.freq = 25.  # Hz.


    def run(self):
        """
        This is where the work happens.
        """
        self.keep_running = True
        time_wait = 1000./self.freq  # milliseconds
        while self.keep_running:
            time_zero = time.time()

            dt, width = self.response.output()
            super(DampedServo, self).pulse(width)

            # Wait until end of time interval.
            time_delta = time_wait - (time.time() - time_zero)
            if time_delta > 0:
                self.sleep(time_delta)

            # Repeat loop.

        print('Servo exit: %d' % self.channel)

        # Done.


    def stop(self):
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

def test_position(value, c0, c1):
    """
    Configure servos at position 0.
    """
    S0 = Servo(c0, info=info_sg5010)
    S1 = Servo(c1, info=info_sg92r)

    print(S0.pulse(value))
    print(S1.pulse(value))

    # Done.




if __name__ == '__main__':
    """
    My little example.
    """

    ###################################
    # Setup.
    tau = .5
    actions = [[ 0.,  0.],
               [ 1., 10.],
               [ 2.,  5.],
               [10.,  0.]]

    time_delta = 0.1

    ###################################
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
