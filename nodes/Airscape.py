

import polyinterface

LOGGER = polyinterface.LOGGER

class Airscape(polyinterface.Node):

    def __init__(self, controller, primary, address, name):
        super(AirscapeNode, self).__init__(controller, primary, address, name)

    def start(self):
        self.setDriver('ST', 1)
        pass

    def setOn(self, command):
        self.setDriver('ST', 1)

    def setOff(self, command):
        self.setDriver('ST', 0)

    def query(self):

        self.reportDrivers()

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 2}]
    id = 'airscape'
    commands = {
        'DON': setOn,
        'DOF': setOff
    }
