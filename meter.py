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
from lib.machine import machine
from lib.infrastructure import infrastructure
from ConfigParser import SafeConfigParser
# import platform
# import cpu-info

def main():
    parser = SafeConfigParser()
    parser.read('cfg/config.info')
    cfg_infr_name = parser.get('infrastructure','name')
    cfg_infr_id = parser.get('infrastructure', 'id')
    cfg_machine_id = parser.get('machine', 'id')

    inf = infrastructure()
    node = machine()

    if cfg_infr_id=="0":
        infr_id = inf.create_infr(cfg_infr_name)
        parser.set('infrastructure','id', str(infr_id))
        cfgfile = open("cfg/config.info",'w')
        parser.write(cfgfile)
        cfgfile.close()
    else:
        infr_id = cfg_infr_id

    if cfg_machine_id=="0":
        machine_id = node.create_machine(inf.org_id, infr_id)
        parser.set('machine', 'id', str(machine_id))
        cfgfile = open("cfg/config.info",'w')
        parser.write(cfgfile)
        cfgfile.close()
    else:
        machine_id = cfg_machine_id

    meter = readings(machine_id, inf.org_id, infr_id)

    meter.gather_metrics()

if __name__ == "__main__":
    main()

#TODO
# update data points - real ones
# get cpu, get disk, get nics
# arrays of nics and disks
# cpu.cpuinfo - speed * cpucount

