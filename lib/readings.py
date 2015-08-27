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
        self.first_run = True
        self.cpu = 0
        self.mem = 0
        self.network = 0
        self.disk_pctg = 0
        self.disk_amt = 0
        self.disk_io = 0
        self.machine_id = machine_id
        self.org_id = org_id
        self.infr_id = infr_id
        self.disk_readings = []
        self.nic_readings = []
        try:
            temp = mach_config['cpu_count']
            self.mach_config = mach_config
        except:
            raise Exception('There is no configuration for this machine available at this time.')

    def gather_metrics(self):
        while True:
            self.insertTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            self.send_metrics()
            time.sleep(10)

    def get_cpu(self):
        self.cpu_percent = psutil.cpu_percent()
        i = 1
        return psutil.cpu_percent()

    def get_memory(self):
        self.memory_used = psutil.virtual_memory().used
        i = 1
        return self.memory_used

    def disk_info(self):

        disk_readings = []

        if 'read_count' in self.mach_config['disks'][0]:
            for current_disk in self.mach_config['disks']:
            
                io_counter = psutil.disk_io_counters()
                total_disk = psutil.disk_usage(current_disk['path'])[0]
                
                kb_read = abs(io_counter[2] - current_disk['read_count']) / 1000
                kb_write = abs(io_counter[3] - current_disk['write_count']) / 1000

                current_disk['read_count'] = io_counter[2]
                current_disk['write_count'] = io_counter[3]
                current_disk['total_count'] = total_disk
    
    
                disk_readings.append({"id": current_disk['disk_id'],
                                           "readings": [
                                               {
                                                   "reading_at": self.insertTime,
                                                   "usage_bytes": total_disk,
                                                   "read_kilobytes": kb_read,
                                                   "write_kilobytes": kb_write
                                               }
                                           ]})
    
                print "\n%s" % self.insertTime
    
                print "disk read: %s" % kb_read
                print "disk write: %s" % kb_write

        else:
            disk_readings.append({"id": self.mach_config['disks'][0]['disk_id'],
                                  "readings": [
                                      {
                                          "reading_at": self.insertTime,
                                          "usage_bytes": 0,
                                          "read_kilobytes": 0,
                                          "write_kilobytes": 0
                                      }
                                  ]})

            io_counter = psutil.disk_io_counters()

            self.mach_config['disks'][0]['read_count'] = io_counter[2]
            self.mach_config['disks'][0]['write_count'] = io_counter[3]
            self.mach_config['disks'][0]['total_count'] = io_counter[2] + io_counter[3]

        return disk_readings

    def nic_info(self):
        nic_readings = []

        if "transmit_count" in self.mach_config['nics'][0]:
            io_counter = psutil.net_io_counters()

            kb_write = abs(io_counter[0] - self.mach_config['nics'][0]['transmit_count']) / 1000
            kb_read = abs(io_counter[1] - self.mach_config['nics'][0]['received_count']) / 1000

            self.mach_config['nics'][0]['transmit_count'] = io_counter[0]
            self.mach_config['nics'][0]['received_count'] = io_counter[1]

            nic_readings.append({"id": self.mach_config['nics'][0]['nic_id'],
                                 "readings": [
                                     {
                                         "reading_at": self.insertTime,
                                         "transmit_kilobits": kb_write,
                                         "receive_kilobits": kb_read
                                     }
                                 ]})

            print "\nReceived: %s" % kb_read
            print "Sent: %s" % kb_write

        else:
            nic_readings.append({"id": self.mach_config['nics'][0],
                                 "readings": [
                                     {
                                         "reading_at": self.insertTime,
                                         "transmit_kilobits": 0,
                                         "receive_kilobits": 0
                                     }
                                 ]})
            io_counter = psutil.net_io_counters()

            self.mach_config['nics'][0]['transmit_count'] = io_counter[0]
            self.mach_config['nics'][0]['received_count'] = io_counter[1]

        return nic_readings

    def send_metrics(self):

        # To Check the Disk and Nic functions are working
        #
        # self.disk_info()
        # self.nic_info()
        #
        # return

        reading_details = {
            "readings": [
                {
                    "reading_at": self.insertTime,
                    "cpu_usage_percent": self.get_cpu(),
                    "memory_bytes": self.get_memory()
                }
            ],
            "disks": self.disk_info(),
            "nics": self.nic_info()
        }

        reading_details_json = json.dumps(reading_details, sort_keys=True, indent=4)

        #todo: fix the post for the readings

        try:

            URI = "https://console.6fusion.com:443/api/v2/"
            URI += "organizations/%s/infrastructures/%s/machines/%s/readings.json" % (
            self.org_id, self.infr_id, self.machine_id)
            URI += "?access_token=%s" % oauth_token
            readingPost = requests.post(URI, data=reading_details_json, headers=headers)
            if self.first_run:
                self.first_run = False
                return
            if readingPost.status_code != 202:
                print "There was an error %s in the update of the machine readings at %s " % (readingPost.status_code,
                                                                                              self.insertTime)

            return

        except Exception as e:
            print('ERROR: ' + str(e))
            raise Exception('Measurement upload failed.  Halting execution')
