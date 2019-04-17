
import polyinterface
import logging
from nodes import Airscape2
from node_funcs import *

LOGGER = polyinterface.LOGGER

class Controller(polyinterface.Controller):
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'Airscape Controller'
        self.hb = 0
        #self.poly.onConfig(self.process_config)

    def start(self):
        LOGGER.info('Started Airscape NodeServer')
        self.set_debug_mode()
        self.check_params()
        self.discover("")
        self.update_profile("")

    def shortPoll(self):
        for node in self.nodes:
            if self.nodes[node].address != self.address and self.nodes[node].do_poll:
                self.nodes[node].shortPoll()

    def longPoll(self):
        for node in self.nodes:
            if self.nodes[node].address != self.address and self.nodes[node].do_poll:
                self.nodes[node].longPoll()
        self.heartbeat()

    def query(self):
        self.check_params()
        for node in self.nodes:
            if self.nodes[node].address != self.address and self.nodes[node].do_poll:
                self.nodes[node].query()
        self.reportDrivers()

    def discover(self, command):
        if self.airscape2 is None or len(self.airscape2) == 0:
            self.l_info('discover','No Airscape 2 Entries in config: {}'.format(self.airscape2))
            return
        for a2 in self.airscape2:
            self.addNode(Airscape2(self, self.address, get_valid_node_name(a2['name']), 'Airscape {}'.format(a2['name']), a2))

    def delete(self):
        LOGGER.info('Oh God I\'m being deleted. Nooooooooooooooooooooooooooooooooooooooooo.')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def heartbeat(self):
        LOGGER.debug('heartbeat hb={}'.format(self.hb))
        if self.hb == 0:
            self.reportCmd("DON",2)
            self.hb = 1
        else:
            self.reportCmd("DOF",2)
            self.hb = 0

    def get_typed_name(self,name):
        typedConfig = self.polyConfig.get('typedCustomData')
        if not typedConfig:
            return None
        return typedConfig.get(name)

    def check_params(self):

        params = [
            {
                'name': 'airscape2',
                'title': 'Airscape 2',
                'desc': 'Airscape 2nd Generation Controller',
                'isList': True,
                'params': [
                    {
                        'name': 'name',
                        'title': "Name",
                        'isRequired': True,
                    },
                    {
                        'name': 'host',
                        'title': 'Host Name or IP Address',
                        'isRequired': True
                    },
                ]
            },
        ]
        self.poly.save_typed_params(params)

        # Remove all existing notices
        self.removeNoticesAll()

        self.airscape2 = self.get_typed_name('airscape2')
        if self.airscape2 is None or len(self.airscape2) == 0:
            self.addNotice('Please add a Airscape 2 Fan in the configuration page','config')

    def remove_notice_config(self,command):
        self.removeNotice('config')

    def update_profile(self,command):
        LOGGER.info('update_profile:')
        st = self.poly.installprofile()
        return st

    def set_all_logs(self,level):
        self.l_info("set_all_logs",level)
        LOGGER.setLevel(level)
        #logging.getLogger('requests').setLevel(level)
        #logging.getLogger('urllib3').setLevel(level)

    def set_debug_mode(self,level=None):
        self.l_info("set_debug_mode",level)
        mdrv = 'GV1'
        if level is None:
            try:
                level = self.getDriver(mdrv)
            except:
                self.l_error('set_debug_mode','getDriver(GV2) failed',True)
            if level is None:
                level = 30
        level = int(level)
        self.debug_mode = level
        try:
            self.setDriver(mdrv, level)
        except:
            self.l_error('set_debug_mode','setDriver(GV2) failed',True)
        self.debug_level = 0
        if level < 20:
            self.set_all_logs(logging.DEBUG)
            # 9 & 8 incrase pgsession debug level
            if level == 9:
                self.debug_level = 1
            elif level == 8:
                self.debug_level = 2
        elif level <= 20:
            self.set_all_logs(logging.INFO)
        elif level <= 30:
            self.set_all_logs(logging.WARNING)
        elif level <= 40:
            self.set_all_logs(logging.ERROR)
        elif level <= 50:
            self.set_all_logs(logging.CRITICAL)
        else:
            self.l_error("set_debug_mode","Unknown level {0}".format(level))
        self.l_info("set_debug_mode"," session debug_level={}".format(self.debug_level))

    def l_info(self, name, string):
        LOGGER.info("%s:%s: %s" %  (self.id,name,string))

    def l_error(self, name, string):
        LOGGER.error("%s:%s: %s" % (self.id,name,string))

    def l_warning(self, name, string):
        LOGGER.warning("%s:%s: %s" % (self.id,name,string))

    def l_debug(self, name, string):
        LOGGER.debug("%s:%s: %s" % (self.id,name,string))

    id = 'controller'
    commands = {
        'QUERY': query,
        'DISCOVER': discover,
        'UPDATE_PROFILE': update_profile,
    }
    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 2}
    ]
