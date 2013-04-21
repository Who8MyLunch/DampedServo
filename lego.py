
import os
import time

import numpy as np
import RPIO

import damped_servo
import beats

########################################

class Controller(object):
    
    def __init__(self, channel_0, scale_0, channel_1, scale_1, fname_song=None):
        
        if fname_song:
            self.player = beats.Player(fname_song)
        else:
            self.player = None
            
        
        self.channel_0 = channel_0
        self.scale_0 = scale_0
        self.D_0 = None
        
        self.channel_1 = channel_1
        self.scale_1 = scale_1
        self.D_1 = None

        self.pin_butt_red = 23
        self.pin_butt_yel = 24
        self.pin_butt_grn = 25

        self.pin_led_red = 4
        self.pin_led_yel = 17
        self.pin_led_grn = 21

        # Done.


    def blink_led(self, pin, value):
        print('Blink LED')

        RPIO.output(self.pin_led_red, False)
        RPIO.output(self.pin_led_yel, False)
        RPIO.output(self.pin_led_grn, False)

        RPIO.output(self.pin_led_red, True)
        time.sleep(0.05)
        RPIO.output(self.pin_led_yel, True)
        time.sleep(0.05)
        RPIO.output(self.pin_led_grn, True)
        
        time.sleep(0.3)

        RPIO.output(self.pin_led_red, False)
        time.sleep(0.05)
        RPIO.output(self.pin_led_yel, False)
        time.sleep(0.05)
        RPIO.output(self.pin_led_grn, False)
    
        # Done.
        

    def callback_end_looping(self, pin, value):
        print('Button: %s, %s.  Stop main loop!' % (pin, value) )
        self.keep_running = False
        
        
    def turn_on(self):
        print('Initialize GPIO pins')
        RPIO.setup(self.pin_led_red, RPIO.OUT)
        RPIO.setup(self.pin_led_yel, RPIO.OUT)
        RPIO.setup(self.pin_led_grn, RPIO.OUT)

        RPIO.setup(self.pin_butt_red, RPIO.IN)
        RPIO.setup(self.pin_butt_yel, RPIO.IN)
        RPIO.setup(self.pin_butt_grn, RPIO.IN)
        
        print('Configure GPIO callback event handlers')
        fn = self.callback_end_looping
        RPIO.add_interrupt_callback(self.pin_butt_red, fn, edge='falling', pull_up_down=RPIO.PUD_UP,
                                    threaded_callback=True, debounce_timeout_ms=100)

        fn = self.blink_led
        RPIO.add_interrupt_callback(self.pin_butt_red, fn, edge='falling', pull_up_down=RPIO.PUD_UP,
                                    threaded_callback=True, debounce_timeout_ms=100)
        RPIO.add_interrupt_callback(self.pin_butt_yel, fn, edge='falling', pull_up_down=RPIO.PUD_UP,
                                    threaded_callback=True, debounce_timeout_ms=100)
        RPIO.add_interrupt_callback(self.pin_butt_grn, fn, edge='falling', pull_up_down=RPIO.PUD_UP,
                                    threaded_callback=True, debounce_timeout_ms=100)

        RPIO.wait_for_interrupts(threaded=True)


        print('Instantiate controller objects')
        self.D_0 = damped_servo.DampedServo(self.channel_0, damped_servo.info_sg5010, self.scale_0)
        self.D_1 = damped_servo.DampedServo(self.channel_1, damped_servo.info_sg92r, self.scale_1)

        self.D_0.start()
        self.D_1.start()

        self.D_0.pulse(0)
        self.D_1.pulse(0)
        
        # Done.
    
    
    def intro(self):
        """
        Introduction motion.
        """
        print('Wake up...')
        
        self.D_0.scale = 0.2
        self.D_1.scale = 0.3

        self.D_0.pulse(0.6)
        time.sleep(0.8)

        self.D_1.pulse(0.9)
        time.sleep(1.0)

        self.D_0.scale = self.scale_0
        self.D_1.scale = self.scale_1
        
        # Done.
        
        
    def main_random(self):
        """
        Main event loop, random motion.
        """
        D_01 = [self.D_0, self.D_1]

        ix = [0, 0, 0, 1, 1]
        self.keep_running = True

        print('Enter main loop...')
        while self.keep_running:
            try:
                dt = np.random.uniform(0.10, 0.5)
                time.sleep(dt)

                i = np.random.random_integers(0, len(ix)-1)
                i = ix[i]

                if i == 0:
                    p = np.random.uniform(0.25, 1.0)
                elif i == 1:
                    p = np.random.uniform(0.10, 1.0)
                    
                D = D_01[i]
                D.pulse(p)

            except KeyboardInterrupt:
                print('\nUser stop!')
                self.keep_running = False

        self.player.stop()
        
        # Done.


    def main_dance(self):
        """
        Main event loop, with music.
        """
        D_01 = [self.D_0, self.D_1]
        self.keep_running = True

        motions = {self.D_0: [0.2, 1.0],
                   self.D_1: [0.1, 0.55, 1.0],
                   }
                   
        ix = 0
       
        try:
            print('Play audio')
            self.player.start()
        
            print('Enter main loop...')
            for b, k in enumerate(player.beats()):
                if not self.keep_running:
                    break
            
                value = k % 2 
                D_1.pulse(p)

        except KeyboardInterrupt:
            print('\nUser stop!')
            self.keep_running = False

        self.player.stop()
        
        # Done.


    def finish(self):
        """
        Final act.
        """
        print('Begin shutdown...')
    
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
    
        print('Stowe...')
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
    fname_song = 'Manic Polka'
    
    channel_0 = 3
    channel_1 = 7
    
    scale_0 = 0.20
    scale_1 = 0.05

    ###################3
    # Do it.
    controller = Controller(channel_0, scale_0, channel_1, scale_1, fname_song=fname_song)
    controller.turn_on()
    controller.intro()
    controller.main()
    controller.finish()
    controller.turn_off()
    
    # Done.
