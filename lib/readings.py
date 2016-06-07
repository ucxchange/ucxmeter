import json
import time

from datetime import datetime
import requests
import psutil
from cpuinfo import cpuinfo
from netifaces import interfaces, ifaddresses, AF_INET
from logFramework import Logger, getCurrentTime

headers = {'content-type': 'application/json'}

logFile = "logs/meter_%s.log" % getCurrentTime()
logger = Logger(appName='meter', logFile=logFile)

class readings(object):
    def __init__ (self, *args):
        """

        :param args:
        :return:
        """

        self.info = args[0]

        self.machine_id = self.info.machine_id
        self.ucx_machine_uuid = self.info.ucx_machine_uuid
        self.session = self.info.session
        self.post_url = "http://console-dev.ucxchange.com/uconsole/metrics/save/%s" % self.ucx_machine_uuid

        self.token = args[0].token
        self.infrastructure_name = args[0].infrastructure_name
        self.infrastructure_org_id = args[0].infrastructure_org_id
        self.infrastructure_id = args[0].infrastructure_id
        self.machine_id = args[0].machine_id
        self.machine_config = args[0].machine.machine_details
        self.user = args[0].user
        self.auth_server = args[0].auth_server

        self.send_metrics_api_url = "measurements"

        self.first_run = True
        self.memory_used = None
        log_header = """timeStamp, cpu_percent, cpu_reading_mhz, mem_bytes, mem_mb, disk_bits, \
disk_usage_gb, disk_read, disk_write, disk_io, nic_read, nic_write, nic_io"""
        print log_header
        logger.log_header(log_header)

        self.cpu_readings = []
        self.memory_readings = []
        self.disk_readings = {}
        self.nic_readings = {}
        self.send_counter = 0

        self.get_cpu_info()
        self.setup_disks()
        self.setup_nics()

    def gather_metrics(self):
        """

        :return:
        """
        try:
            disk_counter = psutil.disk_io_counters()
            current_disk = self.machine_config['disks'][0]['remote_id']
            read_count = disk_counter[2]
            write_count = disk_counter[3]
            self.disk_readings[current_disk] = {'total_disk': [],
                                                'kb_read': [],
                                                'kb_write': [],
                                                'read_count': read_count,
                                                'write_count': write_count}
        except Exception as e:
            pass

        try:
            nic_counter = psutil.net_io_counters()
            if 'nic_id' in self.machine_config['nics'][0].keys():
                nic_id = self.machine_config['nics'][0]['nic_id']
            elif 'remote_id' in self.machine_config['nics'][0].keys():
                nic_id = self.machine_config['nics'][0]['remote_id']
            else:
                return
            self.nic_readings[nic_id] = {'kb_read': [],
                                         'kb_write': [],
                                         'transmit_kb': nic_counter[0],
                                         'receive_kb': nic_counter[1]}
        except Exception as e:
            pass

        while True:
            try:
                # self.insert_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
                self.get_disk_reading()
                self.get_nic_readings()
                self.cpu_readings.append(self.get_cpu())
                self.memory_readings.append(psutil.virtual_memory().total - psutil.virtual_memory().available)
                time.sleep(30)
                # time.sleep(3)
                self.send_counter += 1

                if self.send_counter > 10:
                    self.send_counter = 0
                    self.insert_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:00Z')
                    self.ucx_insert_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:00')
                    self.send_metrics()

            except Exception as e:
                pass
                print ("a reading failed moving on")

    def get_cpu_info(self):
        cpu_count = cpuinfo.get_cpu_info()['count']
        self.cpu_speed = cpuinfo.get_cpu_info()['hz_actual_raw'][0] / 1000000.0 * cpu_count
        i = 1

    def setup_disks(self):
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

        i = 1

    def setup_nics(self):
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
            except Exception as e:
                pass
        i = 1

    def get_auth_token (self):
        self.token = self.session.get(self.auth_server, params={'org_id': self.infrastructure_org_id}).text

    def get_cpu(self):
        """

        :return:
        """
        # self.cpu_readings.append(psutil.cpu_percent())
        return psutil.cpu_percent()

    def get_memory(self):
        """

        :return:
        """
        self.memory_readings.append(psutil.virtual_memory().total - psutil.virtual_memory().available)
        self.memory_used = psutil.virtual_memory().total - psutil.virtual_memory().available
        return self.memory_used

    def get_nic_readings(self):
        """

        :return:
        """
        try:
            nic_counter = psutil.net_io_counters()
            if 'nic_id' in self.machine_config['nics'][0].keys():
                nic_id = self.machine_config['nics'][0]['nic_id']
            elif 'remote_id' in self.machine_config['nics'][0].keys():
                nic_id = self.machine_config['nics'][0]['remote_id']
            else:
                return
            nic_temp = self.nic_readings[nic_id]

            nic_temp['kb_read'].append(abs(nic_counter[0] - nic_temp['transmit_kb']) / 1024)
            nic_temp['kb_write'].append(abs(nic_counter[1] - nic_temp['receive_kb']) / 1024)

            nic_temp['transmit_kb'] = nic_counter[0]
            nic_temp['receive_kb'] = nic_counter[1]

        except Exception as e:
            pass

    def get_disk_reading(self):
        """

        :return:
        """

        for current_disk in self.machine_config['disks']:
            try:
                disk_temp = self.disk_readings[current_disk['remote_id']]
                io_counter = psutil.disk_io_counters()

                disk_temp['total_disk'].append(psutil.disk_usage(current_disk['path'])[1])

                disk_temp['kb_read'].append(abs(io_counter[2] - disk_temp['read_count']) / 1024)
                disk_temp['kb_write'].append(abs(io_counter[3] - disk_temp['write_count']) / 1024)

                disk_temp['read_count'] = io_counter[2]
                disk_temp['write_count'] = io_counter[3]

            except Exception as e:
                pass

    def disk_info(self):
        """

        :return:
        """
        disk_readings = []

        disks = self.disk_readings

        for disk, info in disks.iteritems():
            try:
                total_disk = sum(info['total_disk']) / len(info['total_disk'])
                kb_read = sum(info['kb_read']) / len(info['kb_read'])
                kb_write = sum(info['kb_write']) / len(info['kb_write'])

                disk_readings.append({"id": str(disk),
                                      "readings": [
                                          {
                                              "reading_at": self.insert_time,
                                              "usage_bytes": total_disk,
                                              "read_kilobytes": kb_read,
                                              "write_kilobytes": kb_write
                                          }
                                      ]})
            except Exception as e:

                pass
            info['total_disk'] = []
            info['kb_read'] = []
            info['kb_write'] = []

        return disk_readings

    def nic_info(self):
        """

        :return:
        """
        nic_readings = []

        nics = self.nic_readings

        for nic, info in nics.iteritems():
            kb_read = sum(info['kb_read'])/len(info['kb_read'])
            kb_write = sum(info['kb_write']) / len(info['kb_write'])

            nic_readings.append({"id": str(nic),
                                 "readings": [
                                     {
                                         "reading_at": self.insert_time,
                                         "transmit_kilobits": kb_write,
                                         "receive_kilobits": kb_read
                                     }
                                 ]
                                 }
                                )

            info['kb_read'] = []
            info['kb_write'] = []

        i = 1

        return nic_readings

    def send_metrics(self):
        """
        :return:
        """

        disk_info = self.disk_info()
        disk_read = disk_info[0]['readings'][0]['read_kilobytes']
        disk_write = disk_info[0]['readings'][0]['write_kilobytes']
        disk_usage = disk_info[0]['readings'][0]['usage_bytes']
        disk_usage_gb = int(disk_info[0]['readings'][0]['usage_bytes'] * 9.31322574615E-10)

        disk_io = disk_read + disk_write

        nic_info = self.nic_info()
        nic_read = nic_info[0]['readings'][0]['receive_kilobits']
        nic_write = nic_info[0]['readings'][0]['transmit_kilobits']
        nic_io = nic_read + nic_write

        cpu_info = int(sum(self.cpu_readings) / len(self.cpu_readings))
        cpu_reading_mhz = int(cpu_info * self.cpu_speed) / 100

        mem_info = sum(self.memory_readings) / len(self.memory_readings)
        mem_mb = mem_info / (1024 * 1024)

        self.cpu_readings = []
        self.memory_readings = []

        log_info = "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % \
                   (cpu_info, cpu_reading_mhz, mem_info, mem_mb,
                    disk_usage, disk_usage_gb, disk_read, disk_write, disk_io,
                    nic_read, nic_write, nic_io)
        print log_info
        logger.log(log_info)

        try:
            ucx_reading = {
            "comments": '',
            "data": [
                {
                    "uuid": self.ucx_machine_uuid,
                    "readingTime": self.ucx_insert_time,
                    "cpuMhz": int(cpu_reading_mhz),
                    "memoryMegabytes": mem_mb,
                    "diskIOKilobytes": disk_io,
                    "lanKilobits": nic_io,
                    "wanKilobits": 0,
                    "storageGigabytes": int(disk_usage_gb)
                }
            ]
            }

            ucx_reading_json = json.dumps(ucx_reading, sort_keys=True, indent=4)

            ucx_response = requests.request("POST",
                                    self.post_url,
                                    data=ucx_reading_json,
                                    headers=headers)

            if ucx_response.status_code == 200:
                print("UCX Reading at %s was sent" % self.insert_time)

        except:
            print "UCX POST failed"

        try:
            six_fusion_reading = {
                "readings": [
                    {
                        "reading_at": self.insert_time,
                        "cpu_usage_percent": int(cpu_info),
                        "memory_bytes": mem_info
                    }
                ],
                "disks": disk_info,
                "nics": nic_info
            }

            six_fusion_reading_json = json.dumps(six_fusion_reading, sort_keys=True, indent=4)

            # print(reading_details_json)

            self.get_auth_token()
            uri = "https://console.6fusion.com:443/api/v2/"
            uri += "organizations/%s/infrastructures/%s/machines/%s/readings.json" % (self.infrastructure_org_id,
                                                                                      self.infrastructure_id,
                                                                                      self.machine_id)
            uri += "?access_token=%s" % self.token

            reading_post = requests.post(uri,
                                         data=six_fusion_reading_json,
                                         headers=headers)

            if self.first_run:
                self.first_run = False
                return

            elif reading_post.status_code != 202:
                print("There was an error " + str(reading_post.status_code))
                print("in the update of the Machine readings at:" + self.insert_time)

            else:
                print("6fusion reading at %s was sent" % self.insert_time)

            return

        except Exception as e:
            print('ERROR: ' + str(e))
            raise Exception('Measurement upload failed.  Halting execution')
