import requests
import json
import psutil
from datetime import datetime
import time
from netifaces import interfaces, ifaddresses, AF_INET

headers = {'content-type': 'application/json'}
oauth_token = "30a62bf3a34104c882eaa47655e99fa6b81ea1fd3428fa5f5e43b74b4b0a7729"

class readings(object):
    def __init__(self, machine_id=0, org_id=4196, infr_id=0, mach_config=None):
        self.send_metrics_api_url = "measurements"
        self.cpu = 0
        self.mem = 0
        self.network = 0
        self.disk_pctg = 0
        self.disk_amt = 0
        self.disk_io = 0
        self.machine_id = machine_id
        self.org_id = org_id
        self.infr_id = infr_id
        try:
            temp_json = json.loads(mach_config)
            temp = mach_config['cpu_count']
            self.mach_config = mach_config
        except:
            raise Exception('There is no configuration for this machine available at this time.')

    def gather_metrics(self):
        while True:
            time.sleep(20)
            self.send_metrics()

    def get_cpu(self):
        return psutil.cpu_percent()

    def get_memory(self):
        temp = psutil.virtual_memory().used
        return temp

    def get_disk_io(self):
        print("")

    def disk_info(self):
        # "disks": [
        #   {
        #     "id": 0,
        #     "readings": [
        #       {
        #         "reading_at": "",
        #         "usage_bytes": 0,
        #         "read_kilobytes": 0,
        #         "write_kilobytes": 0
        #       }]
        #   }]
        self.disk_info = []
        disks = psutil.disk_partitions()
        disk_io = psutil.disk_io_counters(perdisk=True)
        disk_io_read_kb = disk_io.read_bytes/1000
        disk_io_write_kb = disk_io.write_bytes/1000
        disk_io_usage_bytes = psutil.disk_usage("/")
        for disk in disks:
            if not disk.fstype:
                continue
                i = 1
            else:
                self.disk_info.append({"id": disk[0],
                                       "readings": [
                                           {"reading_at": self.insertTime,
                                            "usage_bytes": disk_io_usage_bytes[0],
                                            "read_kilobytes": disk_io_read_kb[0],
                                            "write_kilobytes": disk_io_write_kb[0]
                                            }]
                                       })
        i = 1


    def nic_info(self):
        # "nics": [
        #   {
        #     "id": 0,
        #     "readings": [
        #       {
        #         "reading_at": "",
        #         "transmit_kilobits": 0,
        #         "receive_kilobits": 0
        #       }]
        # }]
        self.nics=[]
        for interface in interfaces():
            try:
                for link in ifaddresses(interface)[AF_INET]:
                    self.nics.append({"id": interface,
                                      "readings": [
                                          {"reading_at": self.insertTime,
                                           "transmit_kilobits": interface,
                                           "receive_kilobits": interface
                                           }]
                                      })
            except:
                pass
        i = 1


    def get_disk_percentage(self):
        print("")

    def network_io(self):
        print("")

    def get_disk_id(self):
        try:
            URI = "https://console.6fusion.com:443/api/v2/"
            URI += "organizations/%s/infrastructures/%s/machines/%s/disks?" % (
            self.org_id, self.infr_id, self.machine_id)
            URI += "access_token=%s" % oauth_token
            readingPost = requests.get(URI)
            reqInfo = json.loads(readingPost.text)
            disks = reqInfo['embedded']['disks'][0]['remote_id']
            return disks
        except Exception as e:
            print('ERROR: ' + str(e))
            raise Exception('Measurement upload failed.  Halting execution')

    def get_nic_id(self):
        try:
            URI = "https://console.6fusion.com:443/api/v2/"
            URI += "organizations/%s/infrastructures/%s/machines/%s/nics?" % (
            self.org_id, self.infr_id, self.machine_id)
            URI += "access_token=%s" % oauth_token
            readingPost = requests.get(URI)
            reqInfo = json.loads(readingPost.text)
            nics = reqInfo['embedded']['nics'][0]['remote_id']
            return nics
        except Exception as e:
            print('ERROR: ' + str(e))
            raise Exception('Measurement upload failed.  Halting execution')

    def send_metrics(self):
        self.insertTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        reading_details = {
            "disks": self.disk_info,
            "nics": self.nic_info,
            "readings": [
                {
                    "reading_at": self.insertTime,
                    "cpu_usage_percent": self.get_cpu(),
                    "memory_bytes": self.get_memory()
                }
            ]
        }

    #        self.disk_io = self.get_disk_io()
    #        self.disk_pctg = self.get_disk_percentage()
    #        self.network = self.network_io()
        reading_details_json = json.dumps(reading_details,sort_keys=True,indent=4)
        try:
            URI = "https://console.6fusion.com:443/api/v2/"
            URI += "organizations/%s/infrastructures/%s/machines/%s/readings.json?" % (
            self.org_id, self.infr_id, self.machine_id)
            URI += "access_token=%s" % oauth_token
            reading_data = json.dumps(reading_details_json, ensure_ascii=True)
            readingPost = requests.post(URI, data=reading_data, headers=headers)
            if readingPost.request != 202:
                print("There was an error in the update of the machine readings at " + str(self.insertTime) )
            return
        except Exception as e:
            print('ERROR: ' + str(e))
            raise Exception('Measurement upload failed.  Halting execution')
