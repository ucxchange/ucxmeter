import requests
import json
import psutil
from cpuinfo import cpuinfo
from netifaces import interfaces, ifaddresses, AF_INET
import uuid

headers = {'content-type': 'application/json'}
oauth_token = "30a62bf3a34104c882eaa47655e99fa6b81ea1fd3428fa5f5e43b74b4b0a7729"

class machine(object):
    def __init__(self):
        self.create_machine_uri = ""

    def machine_exist(self, id):
        return 0

    def get_mem(self):
        mem_info = psutil.virtual_memory()
        self.total_memory = mem_info[0]

        i = 1

    def get_cpu_info(self):
        cInfo = cpuinfo.get_cpu_info()
        self.cpu_speed = cInfo['hz_actual_raw'][0]
        self.cores = cInfo['count']
        self.total_cpu_speed = self.cpu_speed * self.cores

        i = 1

    def get_nics(self):
        self.nics = []
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
            total_disk_size = psutil.disk_usage(disk[1])[0]
            self.disk_info.append({"device": disk[0],
                                   "maximum_size_bytes": total_disk_size,
                                   "type": "DISK"})

        i = 1

    def create_machine(self):
        server = "server_" + str(uuid.uuid4())

        machine_details = {
            "name": "%s" % server,
            "virtual_name": server,
            "cpu_count": self.cores,
            "cpu_speed_mhz": self.total_cpu_speed,
            "maximum_memory_bytes": self.total_memory,
            "status": "poweredOn",
            "disks": self.disk_info,
            "nics": self.nics
        }

        print machine_details

        i = 1


def main():
    machineInfo = machine()
    machineInfo.get_cpu_info()
    machineInfo.get_mem()
    machineInfo.get_nics()
    machineInfo.get_disks()

    machineInfo.create_machine()

    i = 1

if __name__ == "__main__":
    main()