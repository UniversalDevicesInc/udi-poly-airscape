#!/usr/bin/env python
"""
This is a NodeServer for Airscape Fans for Polyglot v2 written in Python2/3
"""
import udi_interfance
from nodes import Controller

LOGGER = udi_interface.LOGGER

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([Controller])
        polyglot = polyinterface.Interface('Airscape')
        polyglot.start()
        control = Controller(polyglot, 'controller', 'controller', 'Airscape')
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
