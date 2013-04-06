
import os
import time

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




if __name__ == '__main__':
    """
    My little example.
    """

    ###################################
    # Setup.
    channel_0 = 3
    channel_1 = 7
    
    tau_0 = 1.0
    tau_1 = 0.2
    
    actions = [[ 0.,  0.],
               [ 1., 10.],
               [ 2.,  5.],
               [10.,  0.]]


    time_delta = 0.1

    v = [0.5, 0.6, 1., 0.5, 1., 0., 0.05, 0.1, 0.2, 0.4, 0.8, 0.9, 1., 0.8, 0.9, .5]
    
    ###################################
    # Do it.
    D_0 = damped_servo.DampedServo(channel_0, damped_servo.info_sg5010, tau_0)
    D_1 = damped_servo.DampedServo(channel_1, damped_servo.info_sg92r, tau_1)

    D_0.start()
    D_1.start()

    D_0.pulse(0.5)
    D_1.pulse(0.5)

    time.sleep(1.5)

    1/0
    
    u = v[::-1]

    for a, b in zip(v, u):
        D_0.pulse(a)
        #D_1.pulse(b)

        time.sleep(5)
        
    D_0.stop()
    D_1.stop()
    

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


        