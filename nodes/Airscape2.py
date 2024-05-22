

#
# Airscape API Doc:  https://blog.airscapefans.com/archives/gen-2-controls-api
#
# TODO:
# - Nothing
#
from udi_interface import Node,LOGGER
import time
from pgSession import pgSession

class Airscape2(Node):

    def __init__(self, controller, primary, address, name, config_data):
        super(Airscape2, self).__init__(controller.poly, primary, address, name)
        self.config_data = config_data
        self.debug_level = 1
        self.watching_door = False
        self.session = None
        self.status = {}
        self.driver = {}
        controller.poly.subscribe(controller.poly.START,                  self.handler_start, address) 
        controller.poly.subscribe(controller.poly.POLL,                   self.handler_poll)

    def handler_start(self):
        self.setDriver('GV1', 0)
        LOGGER.info(f'config={self.config_data}')
        self.host = self.config_data['host']
        self.session = pgSession(self,self.name,LOGGER,self.host,debug_level=self.debug_level)
        self.query()
        self.do_poll = True

    def handler_poll(self, polltype):
        if self.session is None:
            LOGGER.warning(f"handler_poll: No session created yet")
            return
        if polltype == 'shortPoll':
            self.short_poll()
        else:
            self.long_poll()

    def short_poll(self):
        LOGGER.debug('...')
        if not self.watching_door:
            self.poll()

    def long_poll(self):
        pass

    def poll(self):
        res = self.session.get('status.json.cgi',{},parse="json")
        self.set_from_response(res)

    def wait_for_response(self):
        # Poll until we have a status
        while not (self.st):
            LOGGER.debug("...")
            self.poll()
            time.sleep(1)

    # XREF from airscape to drivers
    all_dinfo = {
        'fanspd': 'ST',
        'attic_temp': 'CLITEMP',
        'timeremaining': 'TIMEREM',
        'power': 'CPW',
        'doorinprocess': 'GV2',
        'cfm': 'GV3',
        'house_temp': 'GV4',
        'oa_temp': 'GV5',
        'interlock1': 'GV6',
        'interlock2': 'GV7'
    }
    # xref from setfanspd to status.cgi. Why are the different???
    all_xref = {
        'attic': 'attic_temp',
        'inside': 'house_temp',
        'oa': 'oa_temp'
    }
    def set_from_response(self,res):
        LOGGER.debug(f'In: {res}')
        self.st = self.check_response(res)
        self.setDriver('GV1',1 if self.st else 0)
        if self.st:
            rdata = res['data']
            for key, value in self.all_xref.items():
                if key in rdata:
                    rdata[value] = rdata[key]
            for key, driver in self.all_dinfo.items():
                if key in rdata:
                    self.status[key] = rdata[key]
                    if key == 'fanspd':
                        dval = int(rdata[key]) * 10 # *10 if zwave and 1 if Insteon
                    else:
                        dval = rdata[key]
                    self.setDriver(driver,dval)
            # Wait for the door if we are not watching it already
            if not self.watching_door:
                self.watch_door()
        LOGGER.debug(f'Out: {self.status}')

    def check_response(self,res):
        if res is not False and 'code' in res and res['code'] == 200:
            if 'data' in res and res['data'] is not False:
                return True
            else:
                LOGGER.error(f'Got good code: {res}')
        return False

    def watch_door(self):
        cnt = 0
        while int(self.status['doorinprocess']) == 1:
            if cnt > 60:
                LOGGER.error('Timeout waiting for door to open?')
                break
            self.watching_door = True
            LOGGER.debug(f"st={self.status['doorinprocess']}")
            time.sleep(1)
            cnt += 1
            self.poll()
        self.watching_door = False
        LOGGER.debug(f"st={self.status['doorinprocess']}")

    def query(self):
        self.poll()
        self.reportDrivers()

    def setOnI(self, command):
        val = command.get('value')
        LOGGER.info(f'val={val}')
        if val is None:
            speed = 5 # Medium
        else:
            val = int(val)
            if val == 0:
                self.setOff({})
                return
            elif val == 255:
                # Insteon High
                speed = 10
            elif val == 253:
                # Inston Medium
                speed = 5
            elif val == 127:
                # Insteon Medium
                speed = 3
            elif val > 10:
                LOGGER.error(f'Illegal value {val}')
                return
        self.setSpeed(speed)

    def setOnZW(self, command):
        val = command.get('value')
        LOGGER.info(f'val={val}')
        if val is None:
            speed = 4
        else:
            val = int(val)
            if val == 0:
                self.setOff({})
                return
            elif val > 90:
                # High
                speed = 10
            elif val > 80:
                # MediumHigh
                speed = 9
            elif val > 80:
                # Medium
                speed = 8
            elif val > 60:
                # Medium
                speed = 7
            elif val > 50:
                # Medium
                speed = 6
            elif val > 40:
                # Medium
                speed = 5
            elif val > 30:
                # Medium
                speed = 4
            elif val > 20:
                # Medium
                speed = 3
            elif val > 10:
                # Medium
                speed = 2
            elif val > 0:
                # Low
                speed = 1
        self.setSpeed(speed)

    def setOff(self, command):
        LOGGER.info('')
        # The data returned by fanspd is not good xml
        res = self.session.get('fanspd.cgi',{'dir': 4},parse="axml")
        self.set_from_response(res)

    def speedDown(self, command):
        LOGGER.info('')
        # The data returned by fanspd is not good xml
        res = self.session.get('fanspd.cgi',{'dir': 3},parse="axml")
        self.set_from_response(res)

    def speedUp(self, command):
        LOGGER.info('')
        # The data returned by fanspd is not good xml
        res = self.session.get('fanspd.cgi',{'dir': 1},parse="axml")
        self.set_from_response(res)

    def addHour(self, command):
        # The data returned by fanspd is not good xml
        res = self.session.get('fanspd.cgi',{'dir': 2},parse="axml")
        self.set_from_response(res)

    def setSpeed(self,val):
        LOGGER.info(f'val={val}')
        if not self.do_poll:
            LOGGER.debug('waiting for startup to complete')
            while not self.do_poll:
                time.sleep(1)
        if val == 0:
            self.setOff('')
        else:
            self.wait_for_response()
            if 'fanspd' in self.status:
                while val > int(self.status['fanspd']):
                    LOGGER.info(f"current={int(self.status['fanspd'])} request={val}")
                    self.speedUp({})
                    time.sleep(1)
                while val < int(self.status['fanspd']):
                    LOGGER.info(f"current={int(self.status['fanspd'])} request={val}")
                    self.speedDown({})
                    time.sleep(1)
                LOGGER.info(f"current={int(self.status['fanspd'])} request={val}")
            else:
                LOGGER.error('Called before we know the current fanspd, that should not be possible')

    drivers = [
        {'driver': 'ST',  'value': 0, 'uom': 25}, # speed
        {'driver': 'CLITEMP', 'value': 0, 'uom': 17}, # attic_temp
        {'driver': 'TIMEREM', 'value': 0, 'uom': 56}, # minutes
        {'driver': 'CPW', 'value': 0, 'uom': 73}, # watt?
        {'driver': 'GV1', 'value': 0, 'uom': 2}, # Online
        {'driver': 'GV2', 'value': 0, 'uom': 2}, # doorinprocess
        {'driver': 'GV3', 'value': 0, 'uom': 7}, # cfm
        {'driver': 'GV4', 'value': 0, 'uom': 17}, # house_temp
        {'driver': 'GV5', 'value': 0, 'uom': 17}, # oa_temp
        {'driver': 'GV6', 'value': 0, 'uom': 56}, # interlock1
        {'driver': 'GV7', 'value': 0, 'uom': 56}, # interlock2

    ]
    id = 'airscape2_F'
    commands = {
        'FDUP': speedUp,
        'FDDOWN': speedDown,
        'DOF': setOff,
        'DON' : setOnZW,
        'ADD_HOUR': addHour,
    }
    """
    Used 4.17.x.x because Benoit said this for the portal:
        GH will use these settings to set/read the fan speeds.
        const fanSpeedsDef = {
          // This is for fanlinc (Insteon, type 1.x.x.x)
          255: [
            {name: 'Off', maxSpeed: 0},
            {name: 'Low', maxSpeed: 127}, // 1% - 49% / Low
            {name: 'Medium', maxSpeed: 253}, // 50% - 99% / Medium
            {name: 'High', maxSpeed: 255}, // 100% / High
          ],
          // This is for fans using ZWave (type 4.16.x.x)
          100: [
            {name: 'Off', maxSpeed: 0},
            {name: 'Low', maxSpeed: 24}, // 1% - 24% / Low
            {name: 'Medium', maxSpeed: 49}, // 25% - 49% / Medium
            {name: 'MediumHigh', maxSpeed: 74}, // 50% - 74% / Medium-High
            {name: 'High', maxSpeed: 100}, // 75-100% / High
          ],
        };
    Hints See: https://github.com/UniversalDevicesInc/hints
    """
    hint = [4,17,9,1]
