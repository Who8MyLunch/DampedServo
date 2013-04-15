
import os
import time

import numpy as np
import RPIO

import damped_servo


class Controller(object):
    
    def __init__(self, channel_0, scale_0, channel_1, scale_1):
        self.channel_0 = channel_0
        self.scale_0 = scale_0
        self.D_0 = None
        
        self.channel_1 = channel_1
        self.scale_1 = scale_1
        self.D_1 = None

        self.pin_red = 24
        self.pin_green = 25

        self.pin_power = 17
        self.pin_led = 23
        

        # Callback functions,
        pin = self.pin_red
        fn = self.callback_end_looping

        RPIO.cleanup()
        RPIO.add_interrupt_callback(pin, fn, edge='falling', pull_up_down=RPIO.PUD_UP,
                                    threaded_callback=True, debounce_timeout_ms=100)
        RPIO.wait_for_interrupts(threaded=True)

        # Done.

        
    def callback_end_looping(self, pin, value):
        print('callback', pin, value)
        self.keep_running = False
        
        
    def turn_on(self):
        print('Initialize GPIO pins')
        RPIO.setup(self.pin_power, RPIO.OUT)
        RPIO.setup(self.pin_led, RPIO.OUT)

        RPIO.setup(self.pin_red, RPIO.IN)
        RPIO.setup(self.pin_green, RPIO.IN)

        print('Power up servo controller board')
        RPIO.output(self.pin_power, True)

        print('Instantiate controller objects')
        self.D_0 = damped_servo.DampedServo(self.channel_0, damped_servo.info_sg5010, self.scale_0)
        self.D_1 = damped_servo.DampedServo(self.channel_1, damped_servo.info_sg92r, self.scale_1)

        self.D_0.scale = self.scale_0
        self.D_1.scale = self.scale_1
        
        self.D_0.start()
        self.D_1.start()
        
        # Done.
    
    
    def intro(self):
        """
        Introduction motion.
        """
        print('Begin motion')
        
        self.D_0.scale = 0.2
        self.D_1.scale = 0.3

        self.D_0.pulse(0.6)
        time.sleep(0.8)

        self.D_1.pulse(0.9)
        time.sleep(1.0)

        self.D_0.scale = self.scale_0
        self.D_1.scale = self.scale_1
        
        # Done.
        
        
    def main(self):
        """
        Main event loop.
        """
        D_01 = [self.D_0, self.D_1]

        ix = [0, 0, 0, 1, 1]
        self.keep_running = True

        print('Main loop...')
        while self.keep_running:
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
                self.keep_running = False

        # Done.


    def finish(self):
        """
        Final act.
        """
        print('Finish up...')
    
        self.D_0.scale = 0.5
        self.D_1.scale = 0.25
    
        self.D_0.pulse(0.60)
        time.sleep(0.5)
    
        self.D_1.pulse(1.0)
        time.sleep(0.25)
    
        self.D_0.pulse(0)
        time.sleep(1.0)
    
        self.D_0.scale = 0.5
        self.D_0.pulse(0.6)
        time.sleep(0.75)
    
        self.D_1.pulse(0)
        time.sleep(2)
    
        print('Move to stowe position...')
        self.D_1.scale = 0.1
        self.D_1.pulse(0.0)
        time.sleep(0.5)
        
        self.D_0.scale = 0.01
        self.D_0.pulse(0.0)
        
        time.sleep(2.0)

        # Done.


    def turn_off(self):
        """
        Turn off and clean up.
        """

        print('Power down servo controller board')
        RPIO.output(self.pin_power, False)

        print('Shut down controller objects')
        self.D_0.stop()
        self.D_1.stop()

        RPIO.cleanup()

        print('Done.')

        


if __name__ == '__main__':
    """
    My little example.
    """

    ###################################
    # Setup.
    channel_0 = 3
    channel_1 = 7
    
    scale_0 = 0.50
    scale_1 = 0.10

    ###################3
    # Do it.
    controller = Controller(channel_0, scale_0, channel_1, scale_1)
    controller.turn_on()
    controller.intro()
    controller.main()
    controller.finish()
    controller.turn_off()
    
    # Done.
