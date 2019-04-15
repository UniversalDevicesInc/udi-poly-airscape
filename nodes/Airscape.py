

import polyinterface

LOGGER = polyinterface.LOGGER

class Airscape(polyinterface.Node):

    def __init__(self, controller, primary, address, name, config_data):
        super(Airscape, self).__init__(controller, primary, address, name)
        self.config_data = config_data

    def start(self):
        self.setDriver('ST', 1)
        self.l_info('start', 'config={}'.format(self.config_data))
        pass

    def setOn(self, command):
        self.setDriver('ST', 1)

    def setOff(self, command):
        self.setDriver('ST', 0)

    def query(self):
        self.reportDrivers()

    def l_info(self, name, string):
        LOGGER.info("%s:%s: %s" %  (self.id,name,string))

    def l_error(self, name, string):
        LOGGER.error("%s:%s: %s" % (self.id,name,string))

    def l_warning(self, name, string):
        LOGGER.warning("%s:%s: %s" % (self.id,name,string))

    def l_debug(self, name, string):
        LOGGER.debug("%s:%s: %s" % (self.id,name,string))

    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 2}
        {'driver': 'GV1', 'value': 0, 'uom': 56}
    ]
    id = 'airscape'
    commands = {
        'DON': setOn,
        'DOF': setOff
    }
