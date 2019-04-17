

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
        self.status = {}

    def shortPoll(self):
        #if 'doorinprocess' in self.status and int(self.status['doorinprocess']) == 1:
        self.l_debug('shortPoll', '...')
        self.poll()

    def longPoll(self):
        self.l_debug('longPoll', '...')
        self.poll()

    def poll(self):
        res = self.session.get('status.json.cgi',{},parse="json")
        self.set_from_response(res)

    def set_from_response(self,res):
        self.l_debug('set_from_repoinse',"Got: {}".format(res))
        self.st = False
        if res is not False and 'code' in res and res['code'] == 200:
            if 'data' in res and res['data'] is not False:
                self.st = True
                self.status = res['data']
                # Inconsistent names
                if 'attic' in self.status:
                    self.status['attic_temp'] = self.status["attic"]
                if 'inside' in self.status:
                    self.status["house_temp"] = self.status['inside']
                if 'oa' in self.status:
                    self.status["oa_temp"]    = self.status['oa']
                # Set what we got
                if 'fanspd' in self.status:
                    self.setDriver('ST',self.status["fanspd"])
                if 'attic_temp' in self.status:
                    self.setDriver('CLITEMP', self.status["attic_temp"])
                if 'timeremaining' in self.status:
                    self.setDriver('TIMEREM', self.status["timeremaining"])
                if 'power' in self.status:
                    self.setDriver('CPW', self.status["power"])
                if 'doorinprocess' in self.status:
                    if int(self.status['doorinprocess']) == 1:
                        self.status['save_shortPoll'] = self.polyConfig['shortPoll']
                        self.polyConfig['shortPoll'] = 1
                    elif 'save_shortPoll' in self.status
                        self.polyConfig['shortPoll'] = self.status['save_shortPoll']
                    self.setDriver('GV2', self.status["doorinprocess"])
                if 'cfm' in self.status:
                    self.setDriver('GV3', self.status["cfm"])
                if 'house_temp' in self.status:
                    self.setDriver('GV4', self.status["house_temp"])
                if 'oa_temp' in self.status:
                    self.setDriver('GV5', self.status["oa_temp"])
            else:
                self.l_error('set_from_reponse', 'Got good code: {}'.format(res))
        self.setDriver('GV1',1 if self.st else 0)

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
        res = self.session.get('fanspd.cgi',{'dir': 4},parse="axml")
        self.set_from_response(res)

    def speedDown(self, command):
        # The data returned by fanspd is not good xml, so ignore it.
        res = self.session.get('fanspd.cgi',{'dir': 3},parse="axml")
        self.set_from_response(res)

    def speedUp(self, command):
        # The data returned by fanspd is not good xml, so ignore it.
        res = self.session.get('fanspd.cgi',{'dir': 1},parse="axml")
        self.set_from_response(res)

    def addHour(self, command):
        # The data returned by fanspd is not good xml, so ignore it.
        res = self.session.get('fanspd.cgi',{'dir': 2},parse="axml")
        self.set_from_response(res)

    def l_info(self, name, string):
        LOGGER.info("%s:%s:%s: %s" %  (self.id,self.name,name,string))

    def l_error(self, name, string):
        LOGGER.error("%s:%s:%s: %s" % (self.id,self.name,name,string))

    def l_warning(self, name, string):
        LOGGER.warning("%s:%s:%s: %s" % (self.id,self.name,name,string))

    def l_debug(self, name, string):
        LOGGER.debug("%s:%s:%s: %s" % (self.id,self.name,name,string))

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
