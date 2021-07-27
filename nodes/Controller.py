
from udi_interface import Node,LOGGER
import logging
from copy import deepcopy
from nodes import Airscape2
from node_funcs import *

class Controller(Node):
    def __init__(self, poly, primary, address, name):
        super(Controller, self).__init__(polyglot)
        self.hb = 0
        self.Notices = Custom(poly, 'notices')
        self.Data    = Custom(poly, 'customdata')
        self.Parameters      = Custom(polyglot, 'customparams')
        self.Notices         = Custom(polyglot, 'notices')
        self.TypedParameters = Custom(polyglot, 'customtypedparams')
        poly.subscribe(poly.START, self.handler_start, address) 
        poly.subscribe(poly.POLL, self.handler_poll)
        poly.subscribe(poly.ADDNODEDONE, self.handler_add_node_done)
        poly.subscribe(poly.CUSTOMTYPEDPARAMS, self.handler_custom_typed_params)
        poly.subscribe(poly.LOGLEVEL, self.handler_log_level)
        #TODO: Doesn't seem to be implemented yet?
        #poly.addLevelName('Debug + Session Verbose',8)
        #poly.addLevelName('Debug + Session',9)
        poly.ready()
        poly.addNode(self)

    def handler_start(self):
        serverdata = self.poly.get_server_data()
        LOGGER.info(f'Started Airscape NodeServer {serverdata['version']}')'
        self.Notices.clear()
        self.heartbeat()
        self.check_profile()
        self.set_params()
        self.discover("")

    def handler_add_node_done(self, node):
        LOGGER.debug(f'node added {node.address} = {node.name}')

    def handler_poll(self, polltype):
        if polltype == 'shortPoll':
            self.short_poll()
        else:
            self.long_poll()

    def short_poll(self):
        for node in self.nodes:
            if self.nodes[node].address != self.address and self.nodes[node].do_poll:
                self.nodes[node].short_poll()

    def long_poll(self):
        for node in self.nodes:
            if self.nodes[node].address != self.address and self.nodes[node].do_poll:
                self.nodes[node].long_poll()
        self.heartbeat()

    def query(self):
        self.check_params()
        for node in self.nodes:
            if self.nodes[node].address != self.address:
                self.nodes[node].query()
        self.reportDrivers()

    def discover(self, command):
        if self.airscape2 is None or len(self.airscape2) == 0:
            LOGGER.info(f'No Airscape 2 Entries in config: {self.airscape2}')
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

    def set_params(self):
        self.TypedParameters.load( 
            [
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
            ], True)
        self.TypedParams.config = typedParams

    def handler_custom_typed_params():
        self.TypedParameters.load(params)
        self.airscape2 = self.TypedParmameters['airscape2']
        if self.airscape2 is None or len(self.airscape2) == 0:
            self.addNotice('Please add a Airscape 2 Fan in the configuration page','config')

    def update_profile(self,command):
        LOGGER.info('update_profile:')
        st = self.poly.installprofile()
        return st

    def handler_log_level(self,level):
        LOGGER(f'level=level')
        #LOGGER.setLevel(level)
        #logging.getLogger('requests').setLevel(level)
        #logging.getLogger('urllib3').setLevel(level)

    # TODO: Add levels 8 & 9 to config
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

    id = 'controller'
    commands = {
        'QUERY': query,
        'DISCOVER': discover,
        'UPDATE_PROFILE': update_profile,
    }
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
    ]
