
import time
import numpy as np
import damped_servo

channel = 7
S = damped_servo.Servo(channel)

lo = 200
hi = 450


S.pulse(lo)
time.sleep(1)

S.pulse(hi)
