import sys

import requests

from lib.readings import readings
from lib.machine import Machine
from lib.infrastructure import Infrastructure

try:
    from ConfigParser import SafeConfigParser
except:
    from configparser import SafeConfigParser


class Meter(object):
    def __init__ (self):
        self.config_file = 'cfg/config.info'
        self.user = "Meter-Test"
        self.infrastructure_name = None
        self.infrastructure_id = None
        self.infrastructure_exchange = None
        self.infrastructure_org_id = None
        self.auth_server = None
        self.machine_id = None
        self.machine_config = None
        self.machine_json = None
        self.new_machine = None
        self.token = None
        self.session = requests.Session()

    def get_config (self):
        self.parser = SafeConfigParser()
        self.parser.read(self.config_file)
        try:
            self.infrastructure_org_id = int(self.parser.get('Infrastructure', 'org_id'))
            i = 1
        except:
            print ("please change the org_id to the proper setting")
            sys.exit()

        try:
            self.infrastructure_exchange = self.parser.get('Infrastructure', 'exchange')
        except:
            print ("no exchange_if found in the config")
            sys.exit()
        if 'ucx' in self.infrastructure_exchange.lower():
            self.auth_server = 'http://data01.ucxchange.com:5001/'
        elif 'ici' in self.infrastructure_exchange.lower():
            self.auth_server = 'http://data01.icixindia.com:5001/'
        else:
            print ("you need to change the exchange param to UCX or ICIx & run again")
            sys.exit()
        self.get_auth_token()

        try:
            self.infrastructure_id = self.parser.get('Infrastructure', 'infrastructure_id')
            self.infrastructure_name = self.parser.get('Infrastructure', 'infrastructure_name')
        except:
            i = 1

        try:
            self.machine_id = self.parser.get('Machine', 'id')
            if self.machine_id == "None":
                self.machine_id = None
        except:
            i = 1

    def add_machine_config (self):
        file_obj = open(self.config_file, 'w')

        self.parser.set('Machine', 'id', str(self.machine_id))
        self.parser.write(file_obj)
        file_obj.close()

    def get_auth_token (self):
        self.token = self.session.get(self.auth_server,
                                      params={'org_id': self.infrastructure_org_id}).text

    def start (self):
        self.get_config()

        self.infrastructure = Infrastructure(self)
        infra_exists = self.infrastructure.check_infr_exist()
        if not infra_exists:
            self.infrastructure_id = self.infrastructure.create_infrastructure()
            file_obj = open(self.config_file, 'w')
            self.parser.set('Infrastructure', 'infrastructure_id', str(self.infrastructure_id))
            self.parser.write(file_obj)
            file_obj.close()

        self.machine = Machine(self)
        self.machine.machine_exist()

        if self.new_machine:
            self.add_machine_config()

        self.readings = readings(self)
        self.readings.gather_metrics()


def main ():
    meterObj = Meter()
    meterObj.start()


if __name__ == "__main__":
    main()
