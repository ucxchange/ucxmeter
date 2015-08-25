import requests
import json
import psutil

headers = {'content-type': 'application/json'}
oauth_token = "30a62bf3a34104c882eaa47655e99fa6b81ea1fd3428fa5f5e43b74b4b0a7729"

class machine(object):
    def __init__(self):
        self.create_machine_uri = ""

    def machine_exist(self, id):
        return 0

    def create_machine(self, org_id, infr_id):
        uuid = self.create_uuid_for_machine_name()
        machine_details = {
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
            print("Machine exists. Moving onto add measurements/readings.")
        else:
            try:
                URI = "https://console.6fusion.com:443/api/v2/"
                URI += "organizations/%s/infrastructures/%s/machines.json?" % (org_id, infr_id)
                URI += "access_token=%s" % oauth_token
                machine_data = json.dumps(machine_details, ensure_ascii=True)
                machinePost = requests.post(URI, data=machine_data, headers=headers)
                reqInfo = json.loads(machinePost.text)
                machineInfo = reqInfo['remote_id']
                return machineInfo
            except Exception as e:
                print('ERROR: ' + str(e))
                raise Exception('Infrastructure creation failed.  Halting execution')

    def create_uuid_for_machine_name(self):
        return "fdkjfkdjfd"  # combo of base64 for company name, "-", machine identifier - mac perhaps

