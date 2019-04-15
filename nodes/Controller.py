
import polyinterface
from nodes import Airscape
from node_funcs import *

LOGGER = polyinterface.LOGGER

class Controller(polyinterface.Controller):
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'Airscape Controller'
        #self.poly.onConfig(self.process_config)

    def start(self):
        LOGGER.info('Started Airscape NodeServer')
        self.check_params()
        self.discover("")
        self.update_profile("")

    def shortPoll(self):
        pass

    def longPoll(self):
        pass

    def query(self):
        self.check_params()
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self, command):
        if self.airscape2 is None or len(self.airscape2) == 0:
            self.l_info('discover','No Airscape 2 Entries in config: {}'.format(self.airscape2))
        for a2 in self.airscape2:
            self.addNode(Airscape(self, self.address, get_valid_node_name(a2['name']), 'Airscape Node {}'.format(a2['name']), a2))

    def delete(self):
        LOGGER.info('Oh God I\'m being deleted. Nooooooooooooooooooooooooooooooooooooooooo.')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def setDriver(self,driver,value):
        self.driver[driver] = value
        super(Controller, self).setDriver(driver,value)

    def getDriver(self,driver):
        if driver in self.driver:
            return self.driver[driver]
        else:
            return super(Controller, self).getDriver(driver)

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

        # Remove all existing notices
        self.removeNoticesAll()
        # Add a notice if they need to change the user/password from the default.
        self.airscape2 = self.get_typed_name('airscape2')
        if self.airscape2 is None or len(self.airscape2) == 0:
            self.addNotice('Please add a Airscape 2 Fan in the configuration page','config')

    def remove_notice_config(self,command):
        self.removeNotice('config')


    def update_profile(self,command):
        LOGGER.info('update_profile:')
        st = self.poly.installprofile()
        return st


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
