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
# import platform
# import cpu-info

def main():
    inf = infrastructure()
    node = machine()

    infr_id = inf.create_infr("temp")

    machine_id = node.create_machine(inf.org_id, infr_id)

    meter = readings(machine_id, inf.org_id, infr_id)

    meter.gather_metrics()


if __name__ == "__main__":
    main()

#TODO
# build config file
#   config.json (name inf)
# read config file
# create infrastructure
# insert infr, and macine id back into config
# update data points - real ones
# get cpu, get disk, get nics
# arrays of nics and disks
# cpu.cpuinfo - speed * cpucount

