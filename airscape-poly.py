#!/usr/bin/env python
"""
This is a NodeServer for Airscape Fans for Polyglot v2 written in Python2/3
"""
from udi_interface import Interface,LOGGER
from nodes import VERSION, Controller
import sys

if __name__ == "__main__":
    try:
        polyglot = Interface([Controller])
        polyglot.start(VERSION)
        control = Controller(polyglot, 'controller', 'controller', 'Airscape')
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        polyglot.stop()
        sys.exit(0)
