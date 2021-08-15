
from udi_interface import Node,LOGGER,Custom
import logging
from copy import deepcopy
from nodes import Airscape2
from node_funcs import *

class Controller(Node):
    def __init__(self, poly, primary, address, name):
        super(Controller, self).__init__(poly, primary, address, name)
        self.hb = 0
        self.airscape2       = None
        self.Notices         = Custom(poly, 'notices')
        self.Data            = Custom(poly, 'customdata')
        self.Parameters      = Custom(poly, 'customparams')
        self.Notices         = Custom(poly, 'notices')
        self.TypedParameters = Custom(poly, 'customtypedparams')
        self.TypedData       = Custom(poly, 'customtypeddata')
        poly.subscribe(poly.START,                  self.handler_start, address) 
        poly.subscribe(poly.POLL,                   self.handler_poll)
        poly.subscribe(poly.ADDNODEDONE,            self.handler_add_node_done)
        poly.subscribe(self.poly.CUSTOMTYPEDPARAMS, self.handler_typed_params)
        poly.subscribe(self.poly.CUSTOMTYPEDDATA,   self.handler_typed_data)
        poly.subscribe(poly.LOGLEVEL,               self.handler_log_level)
        #TODO: Doesn't seem to be implemented yet?
        #poly.addLevelName('Debug + Session Verbose',8)
        #poly.addLevelName('Debug + Session',9)
        poly.ready()
        poly.addNode(self)

    def handler_start(self):
        #serverdata = self.poly._get_server_data()
        LOGGER.info(f"Started Airscape NodeServer {self.poly.serverdata['version']}")
        self.Notices.clear()
        self.heartbeat()
        self.set_params()
        self.discover("")

    def handler_add_node_done(self, node):
        LOGGER.debug(f'node added {node}')

    def handler_poll(self, polltype):
        if polltype == 'longPoll':
            self.heartbeat()

    def query(self):
        self.check_params()
        nodes = self.poly.getNodes()
        for node in self.nodes:
            if nodes[node].address != self.address:
                nodes[node].query()
        self.reportDrivers()

    def discover(self, command):
        if self.airscape2 is None or len(self.airscape2) == 0:
            LOGGER.info(f'No Airscape 2 Entries in config: {self.airscape2}')
            return
        for a2 in self.airscape2:
            self.poly.addNode(Airscape2(self, self.address, get_valid_node_name(a2['name']), 'Airscape {}'.format(a2['name']), a2))

    def delete(self):
        LOGGER.info('I am being deleted...')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def heartbeat(self):
        LOGGER.debug(f'heartbeat hb={self.hb}')
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

    def handler_typed_params(self,params):
        LOGGER.debug(f'Loading typed params now {params}')
        return

    def handler_typed_data(self,params):
        LOGGER.debug(f'Loading typed data now {params}')
        self.Notices.clear()
        self.TypedData.load(params)
        LOGGER.debug(params)
        self.airscape2 = self.TypedData['airscape2']
        if self.airscape2 is None or len(self.airscape2) == 0:
            msg = 'Please add a Airscape 2 Fan in the configuration page'
            LOGGER.warning(msg)
            self.Notices['config'] = msg

    def handler_log_level(self,level):
        LOGGER.debug(f'level=level')
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
            LOGGER.error(f'Unknown level {level}')
        LOGGER.info(f'session debug_level={self.debug_level}')

    id = 'controller'
    commands = {
        'QUERY': query,
        'DISCOVER': discover,
    }
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
    ]
