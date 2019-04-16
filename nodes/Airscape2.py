

#
# Airscape API Doc:  https://blog.airscapefans.com/archives/gen-2-controls-api

import polyinterface
from pgSession import pgSession

LOGGER = polyinterface.LOGGER

class Airscape2(polyinterface.Node):

    def __init__(self, controller, primary, address, name, config_data):
        super(Airscape2, self).__init__(controller, primary, address, name)
        self.config_data = config_data
        self.debug_level = 1

    def start(self):
        self.driver = {}
        self.setDriver('GV1', 0)
        self.l_info('start', 'config={}'.format(self.config_data))
        self.host = self.config_data['host']
        self.session = pgSession(self,self.name,LOGGER,self.host,debug_level=self.debug_level)
        self.query()

    def setOn(self, command):
        self.setDriver('ST', 1)

    def setOff(self, command):
        self.setDriver('ST', 0)

    def query(self):
        res = self.session.get("status.xml.cgi",{})
        self.l_debug('query',"Got: {}".format(res))
        st = 0
        if res is not False and 'code' in res and res['code'] == 200:
            if 'data' in res:
                self.setDriver('GV1',1)
                rdata = res['data']['airscapewhf']
                self.setDriver('ST',rdata["fanspd"])
            else:
                self.setDriver('GV1',0)
        else:
            self.setDriver('GV1',0)

        self.reportDrivers()

    def setDriver(self,driver,value):
        self.driver[driver] = value
        super(Airscape2, self).setDriver(driver,value)

    def getDriver(self,driver):
        if driver in self.driver:
            return self.driver[driver]
        else:
            return super(Airscape2, self).getDriver(driver)

    def speedDown(self, command):
        # The data returned by fanspd is not good xml, so ignore it.
        res = self.session.get('fanspd.cgi',{'dir': 4},parse=False)
        self.l_debug('query',"Got: {}".format(res))
        cst = int(self.getDriver("ST"))
        if cst > 0:
            self.setDriver("ST",cst-1)

    def speedUp(self, command):
        # The data returned by fanspd is not good xml, so ignore it.
        res = self.session.get('fanspd.cgi',{'dir': 1},parse=False)
        self.l_debug('query',"Got: {}".format(res))
        cst = int(self.getDriver("ST"))
        if cst < 8:
            self.setDriver("ST",cst+1)

    def l_info(self, name, string):
        LOGGER.info("%s:%s: %s" %  (self.id,name,string))

    def l_error(self, name, string):
        LOGGER.error("%s:%s: %s" % (self.id,name,string))

    def l_warning(self, name, string):
        LOGGER.warning("%s:%s: %s" % (self.id,name,string))

    def l_debug(self, name, string):
        LOGGER.debug("%s:%s: %s" % (self.id,name,string))

    drivers = [
        {'driver': 'ST',  'value': 0, 'uom': 56},
        {'driver': 'GV1', 'value': 1, 'uom': 2}
    ]
    id = 'airscape2'
    commands = {
        'FADEUP': speedUp,
        'FADEDOWN': speedDown,
        'DON': speedUp,
        'DOF': speedDown
    }
