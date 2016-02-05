import json
import time

from datetime import datetime
import requests
import psutil

headers = {'content-type': 'application/json'}

class readings(object):
    def __init__ (self, *args):
        """

        :param args:
        :return:
        """

        self.info = args[0]

        self.token = args[0].token
        self.infrastructure_name = args[0].infrastructure_name
        self.infrastructure_org_id = args[0].infrastructure_org_id
        self.infrastructure_id = args[0].infrastructure_id
        self.machine_id = args[0].machine_id
        self.machine_config = args[0].machine.machine_details
        self.user = args[0].user
        self.session = args[0].session
        self.auth_server = args[0].auth_server

        self.send_metrics_api_url = "measurements"

        self.first_run = True
        self.memory_used = None
        self.insert_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        self.cpu_readings = []
        self.memory_readings = []
        self.disk_readings = {}
        self.nic_readings = {}
        self.send_counter = 0

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
                self.insert_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
                self.get_disk_reading()
                self.get_nic_readings()
                self.cpu_readings.append(psutil.cpu_percent())
                self.memory_readings.append(psutil.virtual_memory().total - psutil.virtual_memory().available)
                time.sleep(30)
                # time.sleep(3)
                self.send_counter += 1

                if self.send_counter > 20:
                # if self.send_counter > 4:
                    self.send_counter = 0
                    self.insert_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
                    self.send_metrics()
            except Exception as e:
                pass
                print ("a reading failed moving on")

    def get_auth_token (self):
        i = 1
        self.token = self.session.get(self.auth_server,
                                      params={'org_id': self.infrastructure_org_id}).text
        print self.token

    def get_cpu(self):
        """

        :return:
        """
        self.cpu_readings.append(psutil.cpu_percent())
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

            nic_temp['kb_read'].append(abs(nic_counter[0] - nic_temp['transmit_kb']) / 1000)
            nic_temp['kb_write'].append(abs(nic_counter[1] - nic_temp['receive_kb']) / 1000)

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

                disk_temp['kb_read'].append(abs(io_counter[2] - disk_temp['read_count']) / 1000)
                disk_temp['kb_write'].append(abs(io_counter[3] - disk_temp['write_count']) / 1000)

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

        reading_details = {
            "readings": [
                {
                    "reading_at": self.insert_time,
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

        print(reading_details_json)

        try:
            self.get_auth_token()
            uri = "https://console.6fusion.com:443/api/v2/"
            uri += "organizations/%s/infrastructures/%s/machines/%s/readings.json" % (self.infrastructure_org_id,
                                                                                      self.infrastructure_id,
                                                                                      self.machine_id)
            uri += "?access_token=%s" % self.token

            reading_post = requests.post(uri, data=reading_details_json, headers=headers)
            if self.first_run:
                self.first_run = False
                return
            elif reading_post.status_code != 202:
                print("There was an error " + str(reading_post.status_code))
                print("in the update of the Machine readings at:" + self.insert_time)

            else:
                print("Reading at %s was sent" % self.insert_time)

            return

        except Exception as e:
            print('ERROR: ' + str(e))
            raise Exception('Measurement upload failed.  Halting execution')
