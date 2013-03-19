
import os

def my_gen(info):
    """My little generator."""
    count = 0
    while info['flag']:
        count += 2
        yield count




if __name__ == '__main__':

    info = {'flag': True}

    G = my_gen(info)

    c = 0
    for v in G:
        c += 1
        print(v)

        if c > 5:
            info['flag'] = False
            