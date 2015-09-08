import json
from netifaces import interfaces, ifaddresses, AF_INET
import time
import socket
from datetime import datetime

import requests
import psutil
from cpuinfo import cpuinfo

headers = {'content-type': 'application/json'}
oauth_token = "30a62bf3a34104c882eaa47655e99fa6b81ea1fd3428fa5f5e43b74b4b0a7729"

class machine(object):
    def __init__(self, org_id=4196, infra_id=583, infra_name='new infra 01'):
        # self.oAuth_token = oAuth().updateToken()
        self.org_id = org_id
        self.infra_id = infra_id
        self.infra_name = infra_name
        self.cpu_speed = None
        self.cores = None
        self.total_cpu_speed = None
        self.nics = []
        self.total_memory = None

    def machine_exist(self, machine_id):

        URI = "https://console.6fusion.com:443/api/v2"
        URI += "/organizations/%s/infrastructures/%s/machines/%s.json" % (self.org_id, self.infra_id, machine_id)
        URI += "?access_token=%s" % oauth_token

        req = requests.get(URI)

        if req.status_code == 200:
            return True

        else:
            self.create_machine()

    def get_mem(self):
        mem_info = psutil.virtual_memory()
        self.total_memory = mem_info[0]

        i = 1

    def get_cpu_info(self):
        cpu_info = cpuinfo.get_cpu_info()
        self.cpu_speed = cpu_info['hz_actual_raw'][0] / 1000000.0
        self.cores = cpu_info['count']

        i = 1

    def get_nics(self):
        for interface in interfaces():
            try:
                for link in ifaddresses(interface)[AF_INET]:
                    if '127.0.0.1' == link['addr']:
                        continue
                    self.nics.append({"name": interface,
                                      "link": link['addr'],
                                      "kind": 0,
                                      "mac_address": "aa:aa:aa:aa:aa:aa"})
            except:
                pass

        i = 1

    def get_disks(self):
        self.disk_info = []
        disks = psutil.disk_partitions()
        for disk in disks:
            if not disk.fstype:
                continue
                i = 1
            else:
                total_disk_size = psutil.disk_usage(disk[1])[0]
                self.disk_info.append({"name": disk[0],
                                       "maximum_size_bytes": total_disk_size,
                                       "type": "DISK"})

        i = 1

    def create_machine(self):

        self.get_cpu_info()
        self.get_mem()
        self.get_nics()
        self.get_disks()

        name = socket.gethostname() + '_' + datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        self.machine_details = {
            "name": "%s" % name,
            "virtual_name": name,
            "tags": self.infra_name,
            # "tags": [self.infra_name, 'Rico laptop'],
            "cpu_count": self.cores,
            "cpu_speed_mhz": self.cpu_speed,
            "maximum_memory_bytes": self.total_memory,
            "status": "poweredOn",
            "disks": self.disk_info,
            "nics": self.nics
        }

        self.post_machine()

        return (self.machine_number, self.json_details)

    def post_machine(self):

        URI = "https://console.6fusion.com:443/api/v2/"
        URI += "organizations/%s/infrastructures/%s/machines.json?access_token=%s" % (self.org_id,
                                                                                      self.infra_id,
                                                                                      oauth_token)

        try:
            machine_post = requests.post(URI,
                                         data=json.dumps(self.machine_details,
                                                         sort_keys=True,
                                                         indent=4),
                                         headers=headers)

            req_info = json.loads(machine_post.text)

            self.machine_number = req_info['remote_id']
            self.get_uuid(URI.replace('.json', "/%s.json" % self.machine_number, 1))

        except Exception as e:
            print('ERROR: ' + str(e))
            raise Exception('Infrastructure creation failed.  Halting execution')

    def get_uuid(self, URI):

        disk_uri = URI.replace(".json", "/disks.json", 1)

        nic_uri = URI.replace(".json", "/nics.json", 1)

        time.sleep(1)

        try:
            req = requests.get(disk_uri)
            info = json.loads(req.text)
            for disk in info['embedded']['disks']:
                for d in self.machine_details['disks']:
                    if disk['name'] == d['name']:
                        d['disk_id'] = disk['remote_id']
                    for partition in psutil.disk_partitions():
                        if partition[0] == d['name']:
                            d['path'] = partition[1]

        except:
            print("Disk info get failed")

        try:
            req = requests.get(nic_uri)
            info = json.loads(req.text)

            for nic in info['embedded']['nics']:
                for n in self.machine_details['nics']:
                    if nic['name'] == n['name']:
                        n['nic_id'] = nic['remote_id']

            i = 1

        except:
            print("Nic info get failed")

        self.json_details = json.dumps(self.machine_details, sort_keys=True, indent=4)

        i = 1

    def remove_machine (self, machine_id, org=4196, infra=523):

        URI = "https://console.6fusion.com:443/api/v2"
        URI += "/organizations/%s/infrastructures/%s/machines/%s.json" % (org, infra, machine_id)
        URI += "?access_token=%s" % oauth_token

        req = requests.delete(URI)
        if req.status_code == 204:
            print "machine %s was deleted" % machine_id

        else:
            print "machine %s was not deleted" % machine_id


def main():

    machineInfo = machine()
    # machineInfo.create_machine()
    # machineInfo.get_cpu_info()

    machineInfo.remove_machine(machine_id='554381', infra=594)

    i = 1

if __name__ == "__main__":
    main()
