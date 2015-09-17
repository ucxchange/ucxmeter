import json

import requests

headers = {'content-type': 'application/json'}


class Infrastructure(object):
    def __init__ (self, *args):
        """

        :param args:
        :return:
        """

        self.info = args[0]

        self.token = args[0].token
        self.infrastructure_name = args[0].infrastructure_name
        self.infrastructure_org_id = args[0].infrastructure_org_id
        i = 1

    def check_infr_exist(self):
        """

        :return:
        """
        try:
            uri = "https://console.6fusion.com:443/api/v2/"
            uri += "organizations/%s/infrastructures.json?" % self.infrastructure_org_id
            uri += "access_token=%s&limit=100&offset=0" % self.token
            req = requests.get(uri)
            reqInfo = json.loads(req.text)
            infrastructures = reqInfo['embedded']['infrastructures']
            for inf in infrastructures:
                if inf['name'] == self.infrastructure_name:
                    infraId = inf['remote_id']
                    self.info.infrastructure_id = infraId
                    i = 1
                    return True

            return False

        except Exception as e:
            print('ERROR: ' + str(e))
            print('Infrastructure not found. Creating...')

    def create_infrastructure (self):
        """

        :return:
        """
        infr_details = {
            "name": self.infrastructure_name,
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

        try:
            URI = "https://console.6fusion.com:443/api/v2/"
            URI += "organizations/%s/infrastructures.json?" % (self.infrastructure_org_id)
            URI += "access_token=%s" % self.token

            infra_post = requests.post(URI,
                                       data=json.dumps(infr_details,
                                                       sort_keys=True,
                                                       indent=4),
                                       headers=headers)

            info = infra_post.text
            info = json.loads(info)

            infrInfo = info['remote_id']
            return infrInfo
        except Exception as e:
            print('ERROR: ' + str(e))
            raise Exception('Infrastructure creation failed.  Halting execution')

