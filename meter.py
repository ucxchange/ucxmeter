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

import json
import os
import sys

import requests

from lib.readings import readings
from lib.machine import machine
from lib.infrastructure import infrastructure

try:
    from ConfigParser import SafeConfigParser
except:
    from configparser import SafeConfigParser


def main ():
    config_file = 'cfg/config.info'
    parser = SafeConfigParser()
    try:
        parser.read(config_file)
        cfg_infr_name = parser.get('infrastructure', 'name')
        cfg_machine_id = parser.get('machine', 'id')
        try:
            cfg_org_id = parser.get('infrastructure', 'org_id')
            cfg_infr_id = parser.get('infrastructure', 'id')
            cfg_exch_id = parser.get('infrastructure', 'exchange')
            if cfg_exch_id.lower() == 'ucx':
                auth_server = 'http://test.ucxchange.com:5001/'
            elif 'ici' in cfg_exch_id.lower():
                auth_server = 'http://prod.icixindia.com:5001/'
            else:
                print ("you need to change the exchange param to UCX or ICIx & run again")
                sys.exit()
            s = requests.Session()
            token = s.get(auth_server, params={'user_id': cfg_org_id}).text
        except Exception as e:
            print ("infrastructure ID is not set, please set this in the config.info")

    except:
        if not os.path.exists(os.path.dirname(config_file)):
            os.makedirs(os.path.dirname(config_file))

        cfgfile = open("cfg/config.info", 'w')
        parser.add_section('infrastructure')
        parser.set('infrastructure', 'id', '0')
        parser.set('infrastructure', 'name', 'default')
        parser.set('infrastructure', 'org_id', '0')
        parser.add_section('machine')
        parser.set('machine', 'id', '0')
        parser.set('machine', 'config', '0')
        parser.write(cfgfile)
        cfgfile.close()
        cfg_infr_id = 0
        cfg_machine_id = 0
        cfg_org_id = 0
        cfg_infr_name = 'default'
        i = 1
    try:
        inf = infrastructure(org_id=cfg_org_id, infr_id=cfg_infr_id, token=token)
    except:
        print("No token for you exist, verify the config has your org_id, if so call UCX support")
        sys.exit()

    if not cfg_infr_id or cfg_machine_id == "0":
        infr_id = inf.create_infr(cfg_infr_name)
        parser.set('infrastructure', 'id', str(infr_id))
        cfgfile = open("cfg/config.info", 'w')
        parser.write(cfgfile)
        cfgfile.close()
    else:
        infr_id = cfg_infr_id

    if not cfg_machine_id or cfg_machine_id == "0":
        node = machine(inf.org_id, infr_id, cfg_infr_name, token)
        (machine_id, config) = node.create_machine()
        parser.set('machine', 'id', str(machine_id))
        parser.set('machine', 'config', config)
        cfgfile = open("cfg/config.info", 'w')
        parser.write(cfgfile)
        cfgfile.close()
        config_json = config
    else:
        machine_id = cfg_machine_id
        config_json = parser.get('machine', 'config')

    meter = readings(machine_id, inf.org_id, infr_id, json.loads(config_json), token, auth_server)
    meter.gather_metrics()


if __name__ == "__main__":
    main()
