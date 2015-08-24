# per Delano

# The following are the metrics we use from the exported files:
# cpu.usage.average
# mem.consumed.average
# disk.used.latest
# disk.read.average
# disk.write.average
# net.received.average
# net.transmitted.average
#
# Notes
# When supplying disk.used.latest, the Instance should be set to DISKFILE


import psutil
import urllib2
import requests
import json
from datetime import datetime
#import platform
#import cpu-info

headers = {'content-type': 'application/json'}
oauth_token="30a62bf3a34104c882eaa47655e99fa6b81ea1fd3428fa5f5e43b74b4b0a7729"


class organization(object):
    def __init__(self):
        self.org_id="4196"
        self.infr_id=0

    def check_infr_exist(self,infr_name):
        return 0

    def create_infr(self,infr_name):
        if self.check_infr_exist(""):
            print "Infrastructure exists. Moving onto adding machine."
        else:
            try:
                URI = "https://console.6fusion.com:443/api/v2/"
                URI += "organizations/%s/infrastructures.json?" % (self.org_id)
                URI += "access_token=%s&limit=100&offset=0" % oauth_token

                req = requests.get(URI)
                reqInfo = json.loads(req.text)
                #machineInfo = reqInfo['embedded']['machines']
                i = 1
                infraId = reqInfo['embedded']['infrastructures'][0]['remote_id']
                return str(infraId)
            except Exception as e:
                print 'ERROR: ' + str(e)
                raise Exception('Infrastructure creation failed.  Halting execution')

class machine(object):
    def __init__(self):
        self.create_machine_uri=""

    def machine_exist(self,id):
        return 0

    def create_machine(self,org_id,infr_id):
        uuid=self.create_uuid_for_machine_name()
        machine_details={
          "name": "new",
          "virtual_name": "suckIt",
          "cpu_count": 75,
          "cpu_speed_mhz": 3000,
          "maximum_memory_bytes": psutil.virtual_memory().total,
          "tags": "",
          "status": "",
          "disks": [
            {
              "uuid": "",
              "name": "bootDisk",
              "maximum_size_bytes": 324235,
              "type": ""
            }
          ],
          "nics": [
            {
              "uuid": "",
              "name": "eth0",
              "kind": 0,
              "ip_address": "127.0.0.1",
              "mac_address": "aa:aa:aa:aa:aa:aa"
            }
          ]
        }



        if self.machine_exist(uuid):
            print "Machine exists. Moving onto add measurements/readings."
        else:
            try:
                URI = "https://console.6fusion.com:443/api/v2/"
                URI += "organizations/%s/infrastructures/%s/machines.json?" % (org_id, infr_id)
                URI += "access_token=%s" % oauth_token
                machine_data=json.dumps(machine_details,ensure_ascii=True)
                machinePost = requests.post(URI, data=machine_data, headers=headers)
                reqInfo = json.loads(machinePost.text)
                machineInfo = reqInfo['remote_id']
                return machineInfo
            except Exception as e:
                print 'ERROR: ' + str(e)
                raise Exception('Infrastructure creation failed.  Halting execution')

    def create_uuid_for_machine_name(self):
        return "fdkjfkdjfd"  # combo of base64 for company name, "-", machine identifier - mac perhaps

class readings(object):
    def __init__(self,machine_id,org_id,infr_id):
        self.send_metrics_api_url="measurements"
        self.cpu=0
        self.mem=0
        self.network=0
        self.disk_pctg=0
        self.disk_amt=0
        self.disk_io=0
        self.machine_id=machine_id
        self.org_id=org_id
        self.infr_id=infr_id

    def gather_metrics(self):
        self.disk_id=self.get_disk_id()
        self.nic_id=self.get_nic_id()
        self.cpu=self.get_cpu()
        self.mem=self.get_memory()
        self.disk_io=self.get_disk_io()
        self.disk_pctg=self.get_disk_percentage()
        self.network=self.network_io()
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
            URI += "organizations/%s/infrastructures/%s/machines/%s/disks?" % (self.org_id, self.infr_id,self.machine_id)
            URI += "access_token=%s" % oauth_token
            readingPost = requests.get(URI)
            reqInfo = json.loads(readingPost.text)
            disks = reqInfo['embedded']['disks'][0]['remote_id']
            return disks
        except Exception as e:
            print 'ERROR: ' + str(e)
            raise Exception('Measurement upload failed.  Halting execution')

    def get_nic_id(self):
        try:
            URI = "https://console.6fusion.com:443/api/v2/"
            URI += "organizations/%s/infrastructures/%s/machines/%s/nics?" % (self.org_id, self.infr_id,self.machine_id)
            URI += "access_token=%s" % oauth_token
            readingPost = requests.get(URI)
            reqInfo = json.loads(readingPost.text)
            nics = reqInfo['embedded']['nics'][0]['remote_id']
            return nics
        except Exception as e:
            print 'ERROR: ' + str(e)
            raise Exception('Measurement upload failed.  Halting execution')

    def send_metrics(self):
        insertTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        reading_details={
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
            URI += "organizations/%s/infrastructures/%s/machines/%s/readings.json?" % (self.org_id, self.infr_id,self.machine_id)
            URI += "access_token=%s" % oauth_token
            reading_data=json.dumps(reading_details,ensure_ascii=True)
            readingPost = requests.post(URI, data=reading_data, headers=headers)
            #reqInfo = json.loads(readingPost.text)
            #readingInfo = reqInfo['uuid']
            return
        except Exception as e:
            print 'ERROR: ' + str(e)
            raise Exception('Measurement upload failed.  Halting execution')

def main():
    org=organization()
    node=machine()

    infr_id=org.create_infr("temp")

    machine_id=node.create_machine(org.org_id,infr_id)

    meter=readings(machine_id,org.org_id,infr_id)
#    print meter.get_memory()

    meter.gather_metrics()

if __name__ == "__main__":
    main()
