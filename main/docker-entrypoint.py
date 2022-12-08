#!/usr/bin/python3
from os import getenv
from PiSim900.pisim900 import RSim

if __name__ == '__main__':
    s = RSim(host=getenv('API_HOST'), tty=getenv('TTY_S'))
    s.start(getenv('PWRBTN'))
