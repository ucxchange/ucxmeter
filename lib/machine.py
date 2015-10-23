import json
from netifaces import interfaces, ifaddresses, AF_INET
import time
import socket

from datetime import datetime
import requests
import psutil
from cpuinfo import cpuinfo

headers = {'content-type': 'application/json'}


class Machine(object):
    def __init__ (self, *args):
        """

        :param args:
        :return:
        """

        if len(args) == 0:
            return

        self.info = args[0]

        self.token = args[0].token
        self.infrastructure_name = args[0].infrastructure_name
        self.infrastructure_org_id = args[0].infrastructure_org_id
        self.infrastructure_id = args[0].infrastructure_id
        self.machine_id = args[0].machine_id
        self.user = args[0].user
        self.machine_details = None
        self.json_details = None
        self.disks = None

        self.cpu_speed = None
        self.cores = None
        self.total_cpu_speed = None
        self.nics = []

        self.total_memory = None

    def machine_exist (self):
        """

        :return:
        """

        if self.machine_id:

            uri = "https://console.6fusion.com:443/api/v2"
            uri += "/organizations/%s/infrastructures/%s/machines/%s.json" % (self.infrastructure_org_id,
                                                                              self.infrastructure_id,
                                                                              self.machine_id)
            uri += "?access_token=%s" % self.token

            req = requests.get(uri)

            if req.status_code == 200:
                print ("Machine exists. Getting Settings")

                self.machine_details = json.loads(req.text)

                self.get_nics()
                self.get_disks()

                self.get_uuid(uri)

                print ("Got Disk and Nic Info, moving on to reading")

                return True

        else:
            self.info.new_machine = True
            self.create_machine()
            return False

    def get_mem(self):
        """

        :return:
        """
        mem_info = psutil.virtual_memory()
        self.total_memory = mem_info[0]

    def get_cpu_info(self):
        """

        :return:
        """
        cpu_info = cpuinfo.get_cpu_info()
        self.cpu_speed = cpu_info['hz_actual_raw'][0] / 1000000.0
        self.cores = cpu_info['count']

    def get_nics(self):
        """

        :return:
        """
        for interface in interfaces():
            try:
                for link in ifaddresses(interface)[AF_INET]:
                    if '127.0.0.1' == link['addr']:
                        continue
                    self.nics.append({"name": interface,
                                      "link": link['addr'],
                                      "kind": 0,
                                      "mac_address": "aa:aa:aa:aa:aa:aa"})
            except Exception as e:
                pass

    def get_disks(self):
        """

        :return:
        """
        self.disks = []
        disks = psutil.disk_partitions()
        for disk in disks:
            if not disk.fstype:
                continue
            else:
                total_disk_size = psutil.disk_usage(disk[1])[0]
                self.disks.append({"name": disk[0],
                                   "path": disk[1],
                                   "maximum_size_bytes": total_disk_size,
                                   "type": "DISK"})

    def create_machine(self):
        """

        :return:
        """

        print ("Machine not found, creating Machine")

        self.get_cpu_info()
        self.get_mem()
        self.get_nics()
        self.get_disks()

        name = socket.gethostname() + '_' + datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        self.machine_details = {
            "name": "%s" % socket.gethostname(),
            "virtual_name": name,
            "tags": [self.infrastructure_name, self.user],
            "cpu_count": self.cores,
            "cpu_speed_mhz": self.cpu_speed,
            "maximum_memory_bytes": self.total_memory,
            "status": "poweredOn",
            "disks": self.disks,
            "nics": self.nics
        }

        self.post_machine()

        self.info.machine_id = self.machine_id
        self.info.machine_json = self.json_details
        self.info.machine_config = self.machine_details

    def post_machine(self):
        """

        :return:
        """

        uri = "https://console.6fusion.com:443/api/v2/"
        uri += "organizations/%s/infrastructures/%s/machines.json?access_token=%s" % (self.infrastructure_org_id,
                                                                                      self.infrastructure_id,
                                                                                      self.token)

        try:
            machine_post = requests.post(uri,
                                         data=json.dumps(self.machine_details,
                                                         sort_keys=True,
                                                         indent=4),
                                         headers=headers)

            req_info = json.loads(machine_post.text)

            self.machine_id = req_info['remote_id']
            self.get_uuid(uri.replace('.json', "/%s.json" % self.machine_id, 1))

        except Exception as e:
            print('ERROR: ' + str(e))
            raise Exception('machine creation failed.  Halting execution')

    def get_uuid (self, uri):
        """

        :param uri:
        :return:
        """

        disk_uri = uri.replace(".json", "/disks.json", 1)

        nic_uri = uri.replace(".json", "/nics.json", 1)

        try:
            self.machine_details['disks'] = []
            req = requests.get(disk_uri)
            info = json.loads(req.text)
            for disk in info['embedded']['disks']:
                for d in self.disks:
                    if disk['name'] == d['name']:
                        d['disk_id'] = disk['remote_id']
                for partition in psutil.disk_partitions():
                    if partition[0] == disk['name']:
                        disk['path'] = partition[1]
                        self.machine_details['disks'].append(disk)

        except Exception as e:
            print e
            print("Disk info get failed")

        try:
            self.machine_details['nics'] = []
            req = requests.get(nic_uri)
            info = json.loads(req.text)

            for nic in info['embedded']['nics']:
                for n in self.nics:
                    if nic['name'] == n['name']:
                        self.machine_details['nics'].append(nic)

        except Exception as e:
            print e
            print("Nic info get failed")

        self.json_details = json.dumps(self.machine_details, sort_keys=True, indent=4)

    def remove_machine(self, machine_id=None, org_id=None, infra=None, exch=None):
        """

        :param machine_id:
        :param org_id:
        :param infra:
        :param exch:
        :return:
        """

        if not machine_id or not org_id or not infra or not exch:
            try:
                from ConfigParser import SafeConfigParser
            except:
                from configparser import SafeConfigParser

            config_file = '../cfg/config.info'
            parser = SafeConfigParser()

            parser.read(config_file)
            machine_id = parser.get('Machine', 'id')
            org_id = parser.get('Infrastructure', 'org_id')
            infra = parser.get('Infrastructure', 'id')
            exch = parser.get('Infrastructure', 'exchange')
            if exch.lower() == 'ucx':
                auth_server = 'http://test.ucxchange.com:5001/'
            elif 'ici' in exch.lower():
                auth_server = 'http://prod.icixindia.com:5001/'
            else:
                auth_server = None

        else:
            return

        s = requests.Session()
        token = s.get(auth_server, params={'user_id': org_id}).text

        uri = "https://console.6fusion.com:443/api/v2"
        uri += "/organizations/%s/infrastructures/%s/machines/%s.json" % (org_id, infra, machine_id)
        uri += "?access_token=%s" % token

        req = requests.delete(uri)
        if req.status_code == 204:
            print "Machine %s was deleted" % machine_id

        else:
            print "Machine %s was not deleted" % machine_id

        return


def main():
    """

    :return:
    """

    machine_info = Machine()

    machine_id = None
    org_id = None
    infra = None
    exch = None

    machine_info.remove_machine(machine_id, org_id, infra, exch)


if __name__ == "__main__":
    main()
