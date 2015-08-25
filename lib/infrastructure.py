import requests
import json

headers = {'content-type': 'application/json'}
oauth_token = "30a62bf3a34104c882eaa47655e99fa6b81ea1fd3428fa5f5e43b74b4b0a7729"

class infrastructure(object):
    def __init__(self):
        self.org_id = "4196"
        self.infr_id = 0

    def check_infr_exist(self, infr_name):
        return 0

    def create_infr(self, infr_name):
        if self.check_infr_exist(""):
            print("Infrastructure exists. Moving onto adding machine.")
        else:
            try:
                URI = "https://console.6fusion.com:443/api/v2/"
                URI += "organizations/%s/infrastructures.json?" % (self.org_id)
                URI += "access_token=%s&limit=100&offset=0" % oauth_token

                req = requests.get(URI)
                reqInfo = json.loads(req.text)
                # machineInfo = reqInfo['embedded']['machines']
                i = 1
                infraId = reqInfo['embedded']['infrastructures'][0]['remote_id']
                return str(infraId)
            except Exception as e:
                print('ERROR: ' + str(e))
                raise Exception('Infrastructure creation failed.  Halting execution')
