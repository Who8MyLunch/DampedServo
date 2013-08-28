
"""
Test a few ideas about responding to user input in my Raspberry Pi.

For this example a couple of LEDs and buttons are wired up.
I'm using the cool RPIO feature of setting up a callback function that
gets called when I do something like push a button, or release a button.

"""

import time
import RPIO

ix_power = 17
ix_led = 23
ix_button_red = 24
ix_button_green = 25

info = {'keep_looping': True}


def button_red(gpio_id, val):
    print("red %s: %s" % (gpio_id, val))
    info['keep_looping'] = False

def button_green(gpio_id, val):
    print("green %s: %s" % (gpio_id, val))


# Initialize GPIO interrupt callbacks
RPIO.add_interrupt_callback(ix_button_red, button_red, edge='falling', pull_up_down=RPIO.PUD_UP,
                            threaded_callback=True, debounce_timeout_ms=100)

RPIO.add_interrupt_callback(ix_button_green, button_green, edge='falling', pull_up_down=RPIO.PUD_UP,
                            threaded_callback=True, debounce_timeout_ms=100)

# Enter main event loop.
RPIO.wait_for_interrupts(threaded=True)

while info['keep_looping']:
    time.sleep(0.01)


# Finish,
print('\nExit loop!')

RPIO.cleanup()


print('Done')


