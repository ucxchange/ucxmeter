import requests
import json
import psutil
from cpuinfo import cpuinfo
from netifaces import interfaces, ifaddresses, AF_INET
import uuid

headers = {'content-type': 'application/json'}
oauth_token = "30a62bf3a34104c882eaa47655e99fa6b81ea1fd3428fa5f5e43b74b4b0a7729"

class Machine(object):
    def __init__(self, org_id=4196, infra_id=0):
        self.org_id = org_id
        self.infra_id = infra_id
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
        self.cpu_speed = cpu_info['hz_actual_raw'][0]
        self.cores = cpu_info['count']
        self.total_cpu_speed = self.cpu_speed * self.cores

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

        self.json_details = json.dumps(machine_details, sort_keys=True, indent=4)

        self.post_machine()

        return (self.machine_number, self.json_details)

    def post_machine(self):

        URI = "https://console.6fusion.com:443/api/v2/"
        URI += "organizations/%s/infrastructures/%s/machines.json?access_token=%s" % (self.org_id,
                                                                                      self.infra_id,
                                                                                      oauth_token)

        try:
            machine_post = requests.post(URI, data=self.json_details, headers=headers)
            req_info = json.loads(machine_post.text)
            self.machine_number = req_info['remote_id']

        except Exception as e:
            print('ERROR: ' + str(e))
            raise Exception('Infrastructure creation failed.  Halting execution')

    def remove_machine(self, machine_id):

        URI = "https://console.6fusion.com:443/api/v2"
        URI += "/organizations/%s/infrastructures/%s/machines/%s.json" % (self.org_id, self.infra_id, machine_id)
        URI += "?access_token=%s" % oauth_token

        req = requests.delete(URI)
        if req.status_code == 200:
            print "Machine %s was deleted" % machine_id
        else:
            print "Machine %s was not deleted" % machine_id


def main():
    machineInfo = Machine()

#    machineInfo.remove_machine(machine_id='381041')

    i = 1

if __name__ == "__main__":
    main()
