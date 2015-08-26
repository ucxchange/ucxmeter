import requests
import json

headers = {'content-type': 'application/json'}
oauth_token = "30a62bf3a34104c882eaa47655e99fa6b81ea1fd3428fa5f5e43b74b4b0a7729"

class infrastructure(object):
    def __init__(self):
        self.org_id = "4196"
        self.infr_id = 0

    def check_infr_exist(self, infr_name):
        try:
            URI = "https://console.6fusion.com:443/api/v2/"
            URI += "organizations/%s/infrastructures.json?" % (self.org_id)
            URI += "access_token=%s&limit=100&offset=0" % oauth_token
            req = requests.get(URI)
            reqInfo = json.loads(req.text)
            infrastructures = reqInfo['embedded']['infrastructures']
            for inf in infrastructures:
                if inf['name'] == infr_name:
                    infraId = inf['remote_id']
                    return str(infraId)
            return 0
        except Exception as e:
            print('ERROR: ' + str(e))
            print('Infrastructure not found. Creating...')

    def create_infr(self, infr_name):
        infr_details={
              "name": infr_name,
              "tags": "created automatically by UCX Meter",
              "summary": {},
              "hosts": [
                {}
              ],
              "networks": [
                {}
              ],
              "volumes": [
                {}
              ]
            }

        infr_id = self.check_infr_exist(infr_name)
        if (infr_id==0 or infr_id=="None"):
            try:
                URI = "https://console.6fusion.com:443/api/v2/"
                URI += "organizations/%s/infrastructures.json?" % (self.org_id)
                URI += "access_token=%s" % oauth_token
                infr_data = json.dumps(infr_details, ensure_ascii=True)
                infrPost = requests.post(URI, data=infr_data, headers=headers)
                reqInfo = json.loads(infrPost.text)
                infrInfo = reqInfo['remote_id']
                return infrInfo
            except Exception as e:
                print('ERROR: ' + str(e))
                raise Exception('Infrastructure creation failed.  Halting execution')
        else:
            print("Infrastructure exists. Moving onto adding Machine.")
            return infr_id
