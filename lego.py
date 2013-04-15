
import os
import time

import numpy as np
import RPIO

import damped_servo


class Controller(object):
    
    def __init__(self):
        self.channel_0 = None
        self.scale_0 = None
        
        self.channel_1 = None
        self.scale_1 = None

        self.pin_red = None
        self.pin_green = None

        self.pin_power = None
        self.pin_led = None
        
    def begin(self):
        # 
        pass

    def main(self):
        pass

    def finish(self):
        pass


    


if __name__ == '__main__':
    """
    My little example.
    """

    ###################################
    # Setup.
    gpio_button = 24
    
    channel_0 = 3
    channel_1 = 7
    
    scale_0 = 0.50
    scale_1 = 0.10
        
    ###################################
    # Do it.
    print('Initialize...')

    D_0 = damped_servo.DampedServo(channel_0, damped_servo.info_sg5010, scale_0)
    D_1 = damped_servo.DampedServo(channel_1, damped_servo.info_sg92r, scale_1)
    D_01 = [D_0, D_1]

    print('Move to start position...')
    D_0.start()
    D_1.start()

    D_0.scale = 0.2
    D_1.scale = 0.3

    D_0.pulse(0.6)
    time.sleep(0.8)

    D_1.pulse(1.0)
    time.sleep(1.0)

    ix = [0, 0, 0, 1, 1]
    flag_loop = True

    print('Main loop...')
    D_0.scale = scale_0
    D_1.scale = scale_1
    while flag_loop:
        try:
            dt = np.random.uniform(0.10, 1.0)
            time.sleep(dt)

            i = np.random.random_integers(0, len(ix)-1)
            i = ix[i]

            if i == 0:
                p = np.random.uniform(0.35, 1.0)
            elif i == 1:
                p = np.random.uniform(0.10, 1.0)
                    
            D = D_01[i]
            D.pulse(p)

        except KeyboardInterrupt:
            print('\nUser stop!')
            flag_loop = False
    
    # Finish.
    print('Adjust...')

    D_0.scale = 0.5
    D_1.scale = 0.25

    D_0.pulse(0.60)
    time.sleep(0.5)

    D_1.pulse(1.0)
    time.sleep(0.25)

    D_0.pulse(0)
    time.sleep(1.0)

    D_0.scale = 0.5
    D_0.pulse(0.6)
    time.sleep(0.75)

    D_1.pulse(0)
    time.sleep(2)

    print('Move to stowe position...')
    D_1.scale = 0.1
    D_1.pulse(0.0)
    time.sleep(0.5)
    
    D_0.scale = 0.1
    D_0.pulse(0.0)
    
    time.sleep(2.0)

    print('Shutting down...')
    D_0.stop()
    D_1.stop()

    print('Done.')
    
    # Done.
