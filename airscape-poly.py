#!/usr/bin/env python
"""
This is a NodeServer for Airscape Fans for Polyglot v2 written in Python2/3
"""
import polyinterface
from nodes import Controller

LOGGER = polyinterface.LOGGER

if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('Airscape')
        polyglot.start()
        control = Controller(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
