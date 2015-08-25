import requests
import json
import psutil
from datetime import datetime

headers = {'content-type': 'application/json'}
oauth_token = "30a62bf3a34104c882eaa47655e99fa6b81ea1fd3428fa5f5e43b74b4b0a7729"

class readings(object):
    def __init__(self, machine_id, org_id, infr_id):
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

    def gather_metrics(self):
        self.disk_id = self.get_disk_id()
        self.nic_id = self.get_nic_id()
        self.cpu = self.get_cpu()
        self.mem = self.get_memory()
        self.disk_io = self.get_disk_io()
        self.disk_pctg = self.get_disk_percentage()
        self.network = self.network_io()
        self.send_metrics()

    def get_cpu(self):
        return psutil.cpu_percent()

    def get_memory(self):
        temp = psutil.virtual_memory().used
        return temp

    def get_disk_io(self):
        print("")

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
        insertTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        reading_details = {
            "disks": [
                {
                    "id": self.disk_id,
                    "readings": [
                        {
                            "reading_at": insertTime,
                            "usage_bytes": 0,
                            "read_kilobytes": 0,
                            "write_kilobytes": 0
                        }
                    ]
                }
            ],
            "nics": [
                {
                    "id": self.nic_id,
                    "readings": [
                        {
                            "reading_at": insertTime,
                            "transmit_kilobits": 0,
                            "receive_kilobits": 0
                        }
                    ]
                }
            ],
            "readings": [
                {
                    "reading_at": insertTime,
                    "cpu_usage_percent": self.cpu,
                    "memory_bytes": self.mem
                }
            ]
        }
        try:
            URI = "https://console.6fusion.com:443/api/v2/"
            URI += "organizations/%s/infrastructures/%s/machines/%s/readings.json?" % (
            self.org_id, self.infr_id, self.machine_id)
            URI += "access_token=%s" % oauth_token
            reading_data = json.dumps(reading_details, ensure_ascii=True)
            readingPost = requests.post(URI, data=reading_data, headers=headers)
            # reqInfo = json.loads(readingPost.text)
            # readingInfo = reqInfo['uuid']
            return
        except Exception as e:
            print('ERROR: ' + str(e))
            raise Exception('Measurement upload failed.  Halting execution')
