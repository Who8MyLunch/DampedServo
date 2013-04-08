
import os
import time

import numpy as np

import damped_servo


def test_position(c0, c1):
    """
    Configure servos at position 0.
    """
    S0 = damped_servo.Servo(c0, info=damped_servo.info_sg5010)
    S1 = damped_servo.Servo(c1, info=damped_servo.info_sg92r)

    #print(S0.pulse(value))
    #print(S1.pulse(value))

    return S0, S1
    # Done.


limit_table = [[0.00, 0.00, 0.14],
               [0.10, 0.00, 0.11],
               [0.20, 0.00, 0.10],
               [0.30, 0.00, 0.10],
               [0.40, 0.10, 0.60],
               [0.50, 0.20, 0.65],
               [0.52, 0.30, 0.70],
               [0.55, 0.40, 0.75],
               [0.57, 0.50, 0.80],
               [0.60, 0.50, 0.90],
               [0.65, 0.50, 1.00],
               [0.70, 0.55, 1.00],
               [1.00, 0.60, 1.00],
               [1.01, 0.60, 1.00]]

limit_table = np.asarray(limit_table)

def dynamic_limits(y_work, y_ref):
    """
    Modify servo controls based on external constraints.
    """
    edges_L = limit_table[:-1, 0]
    edges_R = limit_table[1:, 0]

    frac_list = (y_ref - edges_L) / (edges_R - edges_L)

    whr = np.where(np.logical_and(0 <= frac_list, frac_list < 1))
    row = limit_table[whr][0]
    y_lo, y_hi = row[1:]

    y_work_mod = y_lo + (y_hi - y_lo) * y_work
    
    return y_work_mod



def make_limiter(D_ref):
    dl = dynamic_limits
    def limiter(y_work):
        y_ref = D_ref.response.y_now
        y_work_mod = dl(y_work, y_ref)
        return y_work_mod

    # Done.
    return limiter

    
    
if __name__ == '__main__':
    """
    My little example.
    """

    ###################################
    # Setup.
    channel_0 = 3
    channel_1 = 7
    
    scale_0 = 0.50
    scale_1 = 0.25
        
    ###################################
    # Do it.
    D_0 = damped_servo.DampedServo(channel_0, damped_servo.info_sg5010, scale_0)
    D_1 = damped_servo.DampedServo(channel_1, damped_servo.info_sg92r, scale_1)
    D_01 = [D_0, D_1]

    D_0.start()
    D_1.start()

    D_0.pulse(0.9)
    
    flag_loop = True
    while flag_loop:
        try:
            dt = np.random.uniform(0.25, 1.0)
            time.sleep(dt)

            i = np.random.random_integers(0, 1)

            if i == 0:
                p = np.random.uniform(0.40, 1.0)
            elif i == 1:
                p = np.random.uniform(0.25, 1.0)
                    
            D = D_01[i]
            D.pulse(p)

        except KeyboardInterrupt:
            print('\nUser stop!')
            flag_loop = False
    
    # Finish,
    print('Move back to position zero...')
    D_0.scale = 0.2
    D_1.scale = 0.1
    
    D_1.pulse(0)
    time.sleep(0.75)
    D_0.pulse(0)
    time.sleep(2.)
    
    print('Shutting down...')
    D_0.stop()
    D_1.stop()

    # Done.