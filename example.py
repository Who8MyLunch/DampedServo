#!/usr/bin/python

import os
import sys
import time
import numpy as np

path_adafruit = 'Adafruit-Raspberry-Pi-Python-Code/Adafruit_PWM_Servo_Driver'
sys.path.append(os.path.abspath(path_adafruit))

import Adafruit_PWM_Servo_Driver


#######
def lohi(period, width):
  """
  period and width in milliseconds.
  """
  D_min = 0.
  D_max = 2.**12

  # counts per millisecond
  gain = (D_max - D_min) / period

  start = 0
  stop = start + width * gain

  stop = int(np.round(stop))
  
  # Done.
  return start, stop
  
########################################
# Setup.
channels = [15] #, 8, 15]
period = 20 # ms

# Pulse sizes in milliseconds.
pulse_min = 0.8
pulse_zero = 1.5
pulse_max = 2.6

########################################
# Do it.
freq = 1./(period / 1000.) # Hz

pwm = Adafruit_PWM_Servo_Driver.PWM(debug=True)
pwm.setPWMFreq(freq)

dt = 1.

# Reset all channels.
#start, stop = lohi(period, 1.0)
#for c in range(16):
#  pwm.setPWM(c, start, stop)
#time.sleep(dt)

1/0
pwm.setPWM(period, pulse_zero)

try:
  while True:
    # Testing.
    start, stop = lohi(period, pulse_min)
    print(start, stop)
    for c in range(16):
      pwm.setPWM(c, start, stop)
    time.sleep(dt)

    #start, stop = lohi(period, pulse_zero)
    #for c in range(16):
    #  pwm.setPWM(c, start, stop)
    #time.sleep(dt)

    start, stop = lohi(period, pulse_max)
    print(start, stop)
    for c in channels:
      pwm.setPWM(c, start, stop)
    time.sleep(dt)

except KeyboardInterrupt:
  print('User stop')

  
#start, stop = lohi(period, pulse_zero)
#for c in range(16):
#  pwm.setPWM(c, start, stop)



# Done
