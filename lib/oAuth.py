__author__ = 'rrojas'

import httplib2
import json
from oauth2client.client import OAuth2Credentials

class oAuth():
    def __init__(self):
        self.oAuthFile = '../cfg/oAuth.cfg'


    def updateToken(self):

        with open(self.oAuthFile) as data_file:
            data = json.load(data_file)
        jsonCreds = json.dumps(data)
        i = 1

        oAuthCreds = OAuth2Credentials.from_json(jsonCreds)

        try:
            oAuthCreds.refresh(httplib2.Http())

        except:
            print "Token update failed"
            return False

        try:
            newJsonCred = oAuthCreds.to_json()
            tempDict = json.loads(newJsonCred)
            newJsonCred = json.dumps(tempDict, indent=4, sort_keys=True)

            data_file = open(self.oAuthFile, 'r+')
            data_file.write(newJsonCred)
            data_file.truncate()
            data_file.close()

        except:
            print "DB update failed"

        return oAuthCreds.access_token

    def getToken(self):

        newToken = self.updateToken()
        print newToken

        i = 1

def main():

    oAuthObj = oAuth()
    oAuthObj.getToken()


    i = 1

if __name__ == "__main__":
    main()
