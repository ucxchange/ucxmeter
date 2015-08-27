import requests
import json
import psutil
from datetime import datetime
import time

headers = {'content-type': 'application/json'}
oauth_token = "30a62bf3a34104c882eaa47655e99fa6b81ea1fd3428fa5f5e43b74b4b0a7729"

class readings(object):
    def __init__(self, machine_id=0, org_id=4196, infr_id=0, mach_config=None):
        self.send_metrics_api_url = "measurements"
        self.first_run = True

        self.machine_id = machine_id
        self.org_id = org_id
        self.infr_id = infr_id
        self.cpu_readings = []
        self.memory_readings = []
        self.disk_readings = {}
        self.nic_readings = {}
        self.send_counter = 0
        try:
            temp = mach_config['cpu_count']
            self.mach_config = mach_config
        except:
            raise Exception('There is no configuration for this machine available at this time.')

    def gather_metrics(self):
        disk_counters = psutil.disk_io_counters(perdisk=True)
        for current_disk in self.mach_config['disks']:
            for tDisk in disk_counters:
                try:
                    if tDisk.lower() in current_disk['name']:
                        disk_counter = disk_counters[tDisk]
                except:
                    pass
            try:
                self.disk_readings[current_disk['disk_id']] = {'total_disk': [],
                                                           'kb_read': [],
                                                           'kb_write': [],
                                                           'read_count': disk_counter[2],
                                                           'write_count': disk_counter[3]}
            except:
                pass

        nic_counters = psutil.net_io_counters(pernic=True)
        for current_nic in self.mach_config['nics']:
            try:
                nic_counter = nic_counters[current_nic['name']]
                self.nic_readings[current_nic['nic_id']] = {'kb_read': [],
                                                        'kb_write': [],
                                                        'transmit_kb': nic_counter[0],
                                                        'receive_kb': nic_counter[1]}
            except:
                pass

        while True:
            self.insertTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            self.get_disk_reading()
            self.get_nic_readings()
            self.cpu_readings.append(psutil.cpu_percent())
            self.memory_readings.append(psutil.virtual_memory().total - psutil.virtual_memory().available)
            time.sleep(10)
            self.send_counter += 1

            if self.send_counter > 30:
                self.insertTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
                self.send_metrics()
                self.send_counter = 0

    def get_cpu(self):
        self.cpu_readings.append(psutil.cpu_percent())
        i = 1
        return psutil.cpu_percent()

    def get_memory(self):
        self.memory_readings.append(psutil.virtual_memory().total - psutil.virtual_memory().available)
        self.memory_used = psutil.virtual_memory().total - psutil.virtual_memory().available
        i = 1
        return self.memory_used

    def get_nic_readings(self):
        nic_counters = psutil.net_io_counters(pernic=True)
        for current_nic in self.mach_config['nics']:
            try:
                nic_counter = nic_counters[current_nic['name']]

                nTemp = self.nic_readings[current_nic['nic_id']]

                nTemp['kb_read'].append(abs(nic_counter[0] - nTemp['transmit_kb']) / 1000)
                nTemp['kb_write'].append(abs(nic_counter[1] - nTemp['receive_kb']) / 1000)

                nTemp['transmit_kb'] = nic_counter[0]
                nTemp['receive_kb'] = nic_counter[1]

                i = 1
            except:
                pass

    def get_disk_reading(self):

        for current_disk in self.mach_config['disks']:
            dTemp = self.disk_readings[current_disk['disk_id']]
            io_counter = psutil.disk_io_counters()
            dTemp['total_disk'].append(psutil.disk_usage(current_disk['path'])[0])

            dTemp['kb_read'].append(abs(io_counter[2] - dTemp['read_count']) / 1000)
            dTemp['kb_write'].append(abs(io_counter[3] - dTemp['write_count']) / 1000)

            dTemp['read_count'] = io_counter[2]
            dTemp['write_count'] = io_counter[3]

            i = 1

    def disk_info(self):
        disk_readings = []

        disks = self.disk_readings

        for disk, info in disks.iteritems():
            total_disk = sum(info['total_disk']) / len(info['total_disk'])
            kb_read = sum(info['kb_read']) / len(info['kb_read'])
            kb_write = sum(info['kb_write']) / len(info['kb_write'])

            disk_readings.append({"id": str(disk),
                                 "readings": [
                                     {
                                         "reading_at": self.insertTime,
                                         "usage_bytes": total_disk,
                                         "read_kilobytes": kb_read,
                                         "write_kilobytes": kb_write
                                     }
                                 ]})

            info['total_disk'] = []
            info['kb_read'] = []
            info['kb_write'] = []

        i = 1

        return disk_readings

    def nic_info(self):
        nic_readings = []

        nics = self.nic_readings

        for nic, info in nics.iteritems():
            kb_read = sum(info['kb_read'])/len(info['kb_read'])
            kb_write = sum(info['kb_write']) / len(info['kb_write'])

            nic_readings.append({"id": str(nic),
                                 "readings": [
                                     {
                                         "reading_at": self.insertTime,
                                         "transmit_kilobits": kb_write,
                                         "receive_kilobits": kb_read
                                     }
                                 ]})

            info['kb_read'] = []
            info['kb_write'] = []

        i = 1

        return nic_readings

    def send_metrics(self):

        reading_details = {
            "readings": [
                {
                    "reading_at": self.insertTime,
                    "cpu_usage_percent": int(sum(self.cpu_readings) / len(self.cpu_readings)),
                    "memory_bytes": sum(self.memory_readings) / len(self.memory_readings)
                }
            ],
            "disks": self.disk_info(),
            "nics": self.nic_info()
        }
        self.cpu_readings = []
        self.memory_readings = []

        reading_details_json = json.dumps(reading_details, sort_keys=True, indent=4)

        print reading_details_json

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
