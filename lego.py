
import os
import time

import numpy as np
import RPIO

import damped_servo
import beats

########################################

class Controller(object):
    
    def __init__(self,
                 channel_0, scale_0,
                 channel_1, scale_1,
                 channel_2, scale_2,
                 channel_3, scale_3,
                 channel_4, scale_4,
                 lag=0.,
                 channel_lohi=None,
                 fname_song=None):
        
        if fname_song:
            self.player = beats.Player(fname_song, lag=lag)
        else:
            self.player = None
            
        self.channel_lohi = channel_lohi
            
        self.channel_0 = channel_0
        self.scale_0 = scale_0
        self.D_0 = None
        
        self.channel_1 = channel_1
        self.scale_1 = scale_1
        self.D_1 = None

        self.channel_2 = channel_2
        self.scale_2 = scale_2
        self.D_2 = None

        self.channel_3 = channel_3
        self.scale_3 = scale_3
        self.D_3 = None

        self.channel_4 = channel_4
        self.scale_4 = scale_4
        self.D_4 = None

        self.pin_butt_red = 23
        self.pin_butt_yel = 24
        self.pin_butt_grn = 25

        self.pin_led_red = 4
        self.pin_led_yel = 17
        self.pin_led_grn = 21

        # Done.


    def blink_led(self, pin, value):
        """
        Blink the LEDs in an interesting fashion.
        """
        
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
        self.D_0 = damped_servo.DampedServo(self.channel_0, damped_servo.info_sg5010,  self.scale_0)
        self.D_1 = damped_servo.DampedServo(self.channel_1, damped_servo.info_sg92r,   self.scale_1, sign=-1)
        self.D_2 = damped_servo.DampedServo(self.channel_2, damped_servo.info_eflrs60, self.scale_2, sign=-1)
        self.D_3 = damped_servo.DampedServo(self.channel_3, damped_servo.info_eflrs60, self.scale_3, sign=-1)
        self.D_4 = damped_servo.DampedServo(self.channel_4, damped_servo.info_sg92r,   self.scale_4, sign=-1, vmin=230)

        self.D_0.start()
        self.D_1.start()
        self.D_2.start()
        self.D_3.start()
        self.D_4.start()

        self.D_0.pulse(0)
        self.D_1.pulse(0)
        self.D_2.pulse(0)
        self.D_3.pulse(0)
        self.D_4.pulse(0)
        
        # Done.
    
    
    def intro(self):
        """
        Introduction motion.
        """
        time.sleep(0.1)
        
        print('Wake up...')
        
        self.D_0.scale = 0.2
        self.D_1.scale = 0.05

        self.D_2.pulse(0.75)
        self.D_3.pulse(0.75)
        self.D_4.pulse(0.75)
        
        self.D_0.pulse(0.9)
        time.sleep(0.5)

        self.D_1.pulse(0.95)
        time.sleep(2.0)

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
        self.keep_running = True

        #D_beats = [self.D_0, self.D_1]
        #D_segments = [self.D_2, self.D_3, self.D_4]
        D_beats = [self.D_0, self.D_3]
        D_segments = [self.D_2, self.D_1, self.D_4]

        parity = {self.D_0: False,
                  self.D_1: False,
                  self.D_2: False,
                  self.D_3: False,
                  self.D_4: False}

        lohi = {self.D_0: self.channel_lohi[0],
                self.D_1: self.channel_lohi[1],
                self.D_2: self.channel_lohi[2],
                self.D_3: self.channel_lohi[3],
                self.D_4: self.channel_lohi[4]}

        
        ix_beat = 0
        ix_segment = 0
        
        try:
            print('Start audio play')
            self.player.start()
        
            print('Enter main loop...')
            v_old = 0.
            for d in self.player.beats():
                t, k = d[:2]
                
                if not self.keep_running:
                    break

                if k == 'beat':

                    ix_beat += 1
                    ix_beat_mod = ix_beat % len(D_beats)

                    if ix_beat:
                        self.blink_led(0, 0)
                        
                    D = D_beats[ix_beat_mod]
                    parity[D] = not parity[D]
                    value = lohi[D][parity[D]]

                    value_work = value * v_old
                    print('[%6.2fs] %4d  %5.2f %5.2f %5.2f' %
                          (t, D.channel, value, v_old, value_work))

                    if value_work > 1:
                        value_work = 1
                        
                    D.pulse(value_work)
                    
                elif k == 'segment':
                    #print('                %.2f' % v_old)
                    ix_segment += 1
                    ix_segment = ix_segment % len(D_segments)

                    D = D_segments[ix_segment]
                    parity[D] = not parity[D]
                    value = lohi[D][parity[D]]
                    #value = lohi_segments[parity[D]]
                    
                    p, v = d[2]
                    alpha = 0.05
                    v_old = alpha * v_old + (1. - alpha) * v

                    value *= v_old
                    if value > 1:
                        value = 1

                    D.pulse(value)
                else:
                    raise ValueError('Invalid kind: %s' % k)


                    
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

        # Move up.
        self.D_0.scale = 0.5
        self.D_1.scale = 0.25

        self.D_2.scale = 0.1
        self.D_3.scale = 0.1
        self.D_4.scale = 0.1
    
        self.D_2.pulse(0.95)
        self.D_3.pulse(0.75)
        self.D_4.pulse(0.65)

        self.D_0.pulse(0.60)
        time.sleep(0.5)
    
        self.D_1.pulse(1.0)
        time.sleep(0.25)

        # Move down.
        self.D_0.pulse(0)
        time.sleep(1.0)
    
        self.D_0.scale = 0.5
        self.D_0.pulse(0.6)
        time.sleep(0.75)

        self.D_2.pulse(0.0)
        self.D_3.pulse(0.0)
        self.D_4.pulse(0.0)        

        # Move back up.
        self.D_1.pulse(0.1)
        time.sleep(2)
    
        print('Stowe...')

        self.D_2.pulse(1.0)
        self.D_3.pulse(1.0)
        self.D_4.pulse(1.0)        

        self.D_1.scale = 0.1
        self.D_1.pulse(0.0)
        time.sleep(0.5)
        
        self.D_0.scale = 0.1
        self.D_0.pulse(0.0)

        self.D_2.pulse(0.0)
        self.D_3.pulse(0.0)
        self.D_4.pulse(0.0)        

        time.sleep(2.0)

        # Done.


    def turn_off(self):
        """
        Turn off and clean up.
        """

        print('Shut down controller objects')
        self.D_0.stop()
        self.D_1.stop()
        self.D_2.stop()
        self.D_3.stop()
        self.D_4.stop()


        RPIO.cleanup()

        print('Done.')

        


if __name__ == '__main__':
    """
    My little example.
    """

    ###################################
    # Setup.
    #fname_song = 'IronMan.mp3'
    #fname_song = 'Semi-Funk.mp3'                   # hmmm
    #fname_song = 'Flutey_Funk.mp3'                 # nice, too flutey later on.
    #fname_song = 'Oppressive Gloom.mp3'
    #fname_song = 'Whiskey on the Mississippi.mp3'  # nice
    fname_song = 'Rocket.mp3'                      # good dancing  Start with this one.
    #fname_song = 'Disco_con_Tutti.mp3'             # too loud??
    #fname_song = 'Manic Polka.mp3'

    lag = 0.1
    
    channel_0 = 3
    channel_1 = 7
    channel_2 = 15
    channel_3 = 14
    channel_4 = 12
    
    scale_0 = 0.20
    scale_1 = 0.15
    scale_2 = 0.05
    scale_3 = 0.05
    scale_4 = 0.025

    lohi = [[0.3, 0.8],
            [0.0, 1.0],
            [0.1, 0.5],
            [0.3, 0.7],
            [0.5, 0.9]]

            
    
    ###################3
    # Do it.
    controller = Controller(channel_0, scale_0,
                            channel_1, scale_1,
                            channel_2, scale_2,
                            channel_3, scale_3,
                            channel_4, scale_4,
                            lag=lag,
                            channel_lohi=lohi,
                            fname_song=fname_song)
    controller.turn_on()
    controller.intro()
    controller.main_dance()
    controller.finish()
    controller.turn_off()
    
    # Done.
