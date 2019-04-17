

#
# Airscape API Doc:  https://blog.airscapefans.com/archives/gen-2-controls-api
#
# TODO:
# - Default shortPoll/longPoll shorter, query faster while doorinmotion?
# - Parse weird xml data from fanspd.cgi
# - If doorinprocess then tight loop to watch when speed increases or decreases?
#
#
import polyinterface
from pgSession import pgSession

LOGGER = polyinterface.LOGGER

class Airscape2(polyinterface.Node):

    def __init__(self, controller, primary, address, name, config_data):
        super(Airscape2, self).__init__(controller, primary, address, name)
        self.config_data = config_data
        self.debug_level = 1
        self.do_poll = False # Don't let shortPoll happen during initialiation

    def start(self):
        self.driver = {}
        self.setDriver('GV1', 0)
        self.l_info('start', 'config={}'.format(self.config_data))
        self.host = self.config_data['host']
        self.session = pgSession(self,self.name,LOGGER,self.host,debug_level=self.debug_level)
        self.query()
        self.do_poll = True

    def shortPoll(self):
        self.poll()

    def longPoll(self):
        self.poll()

    def poll(self):
        res = self.session.get("status.xml.cgi",{})
        self.l_debug('query',"Got: {}".format(res))
        st = 0
        if res is not False and 'code' in res and res['code'] == 200:
            if 'data' in res:
                self.setDriver('GV1',1)
                rdata = res['data']['airscapewhf']
                self.setDriver('ST',rdata["fanspd"])
                self.setDriver('CLITEMP', rdata["attic_temp"])
                self.setDriver('TIMEREM', rdata["timeremaining"])
                self.setDriver('CPW', rdata["power"])
                self.setDriver('GV2', rdata["doorinprocess"])
                self.setDriver('GV3', rdata["cfm"])
                self.setDriver('GV4', rdata["house_temp"])
                self.setDriver('GV5', rdata["oa_temp"])
            else:
                self.setDriver('GV1',0)
        else:
            self.setDriver('GV1',0)

    def query(self):
        self.poll()
        self.reportDrivers()

    def setDriver(self,driver,value):
        self.driver[driver] = value
        super(Airscape2, self).setDriver(driver,value)

    def getDriver(self,driver):
        if driver in self.driver:
            return self.driver[driver]
        else:
            return super(Airscape2, self).getDriver(driver)

    def setOff(self, command):
        # The data returned by fanspd is not good xml, so ignore it.
        res = self.session.get('fanspd.cgi',{'dir': 4},parse=False)
        self.l_debug('query',"Got: {}".format(res))
        if res is not False and res['code'] == 200:
            self.setDriver("ST",0)

    def speedDown(self, command):
        # The data returned by fanspd is not good xml, so ignore it.
        res = self.session.get('fanspd.cgi',{'dir': 3},parse=False)
        self.l_debug('query',"Got: {}".format(res))
        if res is not False and res['code'] == 200:
            cst = int(self.getDriver("ST"))
            if cst > 0:
                self.setDriver("ST",cst-1)

    def speedUp(self, command):
        # The data returned by fanspd is not good xml, so ignore it.
        res = self.session.get('fanspd.cgi',{'dir': 1},parse=False)
        self.l_debug('query',"Got: {}".format(res))
        if res is not False and res['code'] == 200:
            cst = int(self.getDriver("ST"))
            if cst < 8:
                self.setDriver("ST",cst+1)

    def addHour(self, command):
        # The data returned by fanspd is not good xml, so ignore it.
        res = self.session.get('fanspd.cgi',{'dir': 2},parse=False)
        self.l_debug('query',"Got: {}".format(res))


    def l_info(self, name, string):
        LOGGER.info("%s:%s: %s" %  (self.id,name,string))

    def l_error(self, name, string):
        LOGGER.error("%s:%s: %s" % (self.id,name,string))

    def l_warning(self, name, string):
        LOGGER.warning("%s:%s: %s" % (self.id,name,string))

    def l_debug(self, name, string):
        LOGGER.debug("%s:%s: %s" % (self.id,name,string))

    drivers = [
        {'driver': 'ST',  'value': 0, 'uom': 56}, # speed
        {'driver': 'CLITEMP', 'value': 0, 'uom': 17}, # attic_temp
        {'driver': 'TIMEREM', 'value': 0, 'uom': 20}, # hours
        {'driver': 'CPW', 'value': 0, 'uom': 73}, # watt?
        {'driver': 'GV1', 'value': 0, 'uom': 2}, # Online
        {'driver': 'GV2', 'value': 0, 'uom': 2}, # doorinprocess
        {'driver': 'GV3', 'value': 0, 'uom': 7}, # cfm
        {'driver': 'GV4', 'value': 0, 'uom': 17}, # house_temp
        {'driver': 'GV5', 'value': 0, 'uom': 17}, # oa_temp

    ]
    id = 'airscape2_F'
    commands = {
        'FDUP': speedUp,
        'FDDOWN': speedDown,
        'DOF': setOff,
        'ADD_HOUR': addHour,
    }
