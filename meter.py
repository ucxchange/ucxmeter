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

from lib.readings import readings
from lib.machine import Machine
from lib.infrastructure import infrastructure
from ConfigParser import SafeConfigParser
import json

def main():
    parser = SafeConfigParser()
    try:
        parser.read('cfg/config.info')
        cfg_infr_name = parser.get('infrastructure','name')
        cfg_infr_id = parser.get('infrastructure', 'id')
        cfg_machine_id = parser.get('Machine', 'id')
    except:
        cfgfile = open("cfg/config.info",'w')
        parser.set('infrastructure','id', '0')
        parser.set('infrastructure','name', 'change_me')
        parser.set('Machine','id', '0')
        parser.write(cfgfile)
        cfgfile.close()

    inf = infrastructure()


    if (cfg_infr_id=="0" or cfg_infr_id=="None"):
        infr_id = inf.create_infr(cfg_infr_name)
        parser.set('infrastructure','id', str(infr_id))
        cfgfile = open("cfg/config.info",'w')
        parser.write(cfgfile)
        cfgfile.close()
    else:
        infr_id = cfg_infr_id

    if (cfg_machine_id=="0" or cfg_machine_id=="None"):
        node = Machine(inf.org_id, infr_id)
        (machine_id, config) = node.create_machine()
        parser.set('Machine', 'id', str(machine_id))
        parser.set('Machine', 'config', config)
        cfgfile = open("cfg/config.info",'w')
        parser.write(cfgfile)
        cfgfile.close()
        config_json=json.dumps(config)
    else:
        machine_id = cfg_machine_id
        config_json = parser.get('Machine','config')

    meter = readings(machine_id, inf.org_id, infr_id, json.loads(config_json))
    meter.gather_metrics()

if __name__ == "__main__":
    main()


