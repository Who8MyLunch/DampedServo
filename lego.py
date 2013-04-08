
import os
import time

import numpy as np

import damped_servo


def test_position(value, c0, c1):
    """
    Configure servos at position 0.
    """
    S0 = Servo(c0, info=info_sg5010)
    S1 = Servo(c1, info=info_sg92r)

    print(S0.pulse(value))
    print(S1.pulse(value))

    # Done.


limit_table = [[0.00, 0.00, 0.18],
               [0.10, 0.00, 0.15],
               [0.20, 0.00, 0.12],
               [0.30, 0.00, 0.11],
               [0.40, 0.00, 0.10],
               [0.50, 0.00, 0.08],
               [0.55, 0.00, 0.10],
               [0.60, 0.00, 0.30],
               [0.65, 0.00, 0.35],
               [0.70, 0.00, 1.00],
               [1.00, 0.00, 1.00],
               [1.01, 0.00, 1.00]]

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
    def limiter(y_work):
        y_ref = D_ref.response.y_now
        y_work_mod = dynamic_limits(y_work, y_ref)
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
    
    scale_0 = 0.5
    scale_1 = 0.2
    

    time_delta = 1.

    #v = [0.5, 0.6, 1., 0.5, 1., 0., 0.05, 0.1, 0.2, 0.4, 0.8, 0.9, 1., 0.8, 0.9, .5]
    #v = [0., 1., 0.0, 1., 0., 0.5, 1.0, 0.5, 0.0, 0.5, 0., 0.5, 0., 0.5, 0., 0.5, 0.]
    v = [0., 1., 0.5, 0.0]
    
    ###################################
    # Do it.
    D_0 = damped_servo.DampedServo(channel_0, damped_servo.info_sg5010, scale_0)
    limiter = make_limiter(D_0)

    D_1 = damped_servo.DampedServo(channel_1, damped_servo.info_sg92r, scale_1, limiter=limiter)

    D_0.start()
    D_1.start()

    
    u = v[::-1]

    for a, b in zip(v, u):
        D_0.pulse(a)
        D_1.pulse(b)
        
        time.sleep(time_delta)


    time.sleep(2.)

    print('')
    D_0.stop()
    D_1.stop()
    print('')

    if False:
        time_action, y_action = actions.pop(0)

        time_zero = time.time()
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


        