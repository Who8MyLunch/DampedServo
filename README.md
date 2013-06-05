DampedServo
===========

I have always wanted to control something interesting involving little servo
motors.  That's somewhat of an ill-defined dream, isn't it? But it has all
been made possible by using my handy dandy Raspberry Pi computer, five servos,
and my son's Lego blocks.  I built a dancing robot arm and synchronized its
motion to some funky music.

Full details are available on my blog post: http://www.smokedbits.com/2013/05/dancing-lego-and-five-servos.html

Files
-----
  - damped_servo.py: Classes for controlling individual servos with natural motion.
  - beats.py: Functions for analyzing music contained in user-supplied audio files.
  - lego.py: Main dance controller tying together serovo control with timing derived from music beats.

Dependencies
------------
  - numpy - http://www.numpy.org
  - scipy - http://www.scipy.org
  - pyyaml -  http://pyyaml.org/
  - Requests - http://docs.python-requests.org/en/latest/
  - pyechonest - https://github.com/echonest/pyechonest
  - Adafruit library - https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code
  - RPIO - https://pypi.python.org/pypi/RPIO

Information
-----------
  - Technical write up: http://www.smokedbits.com/2013/05/dancing-lego-and-five-servos.html
  - Awesome video: http://youtu.be/lxUSZIiILp0 (special appearance by Lego Batman)
