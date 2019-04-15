#!/usr/bin/env python
"""
This is a NodeServer for Airscape Fans for Polyglot v2 written in Python2/3
"""
import polyinterface

LOGGER = polyinterface.LOGGER

class Controller(polyinterface.Controller):
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'Airscape Controller'
        self.poly.onConfig(self.process_config)

    def start(self):
        LOGGER.info('Started Airscape NodeServer')
        self.addNotice({'hello': 'Hello Friends!'})
        self.check_params()
        self.discover()
        self.poly.add_custom_config_docs("<b>And this is some custom config data</b>")

    def shortPoll(self):
        pass

    def longPoll(self):
        pass

    def query(self):
        self.check_params()
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        self.addNode(AirscapeNode(self, self.address, 'airscapeaddr', 'Airscape Node Name'))

    def delete(self):
        LOGGER.info('Oh God I\'m being deleted. Nooooooooooooooooooooooooooooooooooooooooo.')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def check_params(self):
        """
        This is an example if using custom Params for user and password and an example with a Dictionary
        """
        default_user = "YourUserName"
        default_password = "YourPassword"
        if 'user' in self.polyConfig['customParams']:
            self.user = self.polyConfig['customParams']['user']
        else:
            self.user = default_user
            LOGGER.error('check_params: user not defined in customParams, please add it.  Using {}'.format(self.user))
            st = False

        if 'password' in self.polyConfig['customParams']:
            self.password = self.polyConfig['customParams']['password']
        else:
            self.password = default_password
            LOGGER.error('check_params: password not defined in customParams, please add it.  Using {}'.format(self.password))
            st = False

        # Make sure they are in the params
        self.addCustomParam({'password': self.password, 'user': self.user, 'some_example': '{ "type": "TheType", "host": "host_or_IP", "port": "port_number" }'})

        # Remove all existing notices
        self.removeNoticesAll()
        # Add a notice if they need to change the user/password from the default.
        if self.user == default_user or self.password == default_password:
            # This doesn't pass a key to test the old way.
            self.addNotice('Please set proper user and password in configuration page, and restart this nodeserver','config')

    def remove_notice_config(self,command):
        self.removeNotice('config')


    def update_profile(self,command):
        LOGGER.info('update_profile:')
        st = self.poly.installprofile()
        return st

    id = 'controller'
    commands = {
        'QUERY': query,
        'DISCOVER': discover,
        'UPDATE_PROFILE': update_profile,
    }
    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 2}
    ]


class AirscapeNode(polyinterface.Node):

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

if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('Airscape')
        polyglot.start()
        control = Controller(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
