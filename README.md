# ucxmeter

How to install the meter: (what does this automation do)

1. To run the meter certain packages must be present.  To accomplish this we do the following:
  a. log into you linux or windows node
  b. install the following using apt or yum or windows installers:
    1. python
    2. python-pip
    3. curl
    4. python-dev
    
    example: sudo apt-get install python

3. Pull the latest version of the UCX meter from our source control on github.  You must use the 'prod' branch
  a. change directory to /var
  b. clone the ucxmeter github repository
  
  example: cd /var; git clone -b prod https://github.com/ucxchange/ucxmeter.git . 

2. Change the name of the path where the meter was just cloned to ucx_meter
  example: mv /var/ucxmeter /var/ucx_meter

3. Change the ownership of the meter to a user with priviledges to execute python programs.    
  example: /bin/chown -R ubuntu:ubuntu /var/ucx_meter

4. Change the mode of the ucx meter service file
  example: chmod +x /var/ucx_meter/cfg/ucx-meter-service

4. Change the mode of the ucx meter service daemon file
  example: chmod +x /var/ucx_meter/cfg/run-meter

5. Create your initial meter configuration file.

  example: 
    echo "[infrastructure]
    id = 0
    name = 
  
    [machine]
    id = 0
    config = 0" > /var/ucx_meter/cfg/config.info

6. Download and install pyhton 2.7
- name: prereq python1 - download ez-setup python 2.7
  example: 
    curl -o /tmp/ez_setup.py https://bootstrap.pypa.io/ez_setup.py
    /usr/bin/python2.7 /tmp/ez_setup.py

7. Install the following python libraries
  example: 
    pip2 install psutil
    pip2 install py-cpuinfo
    pip2 install netifaces

8. Start the meter
  example:
    /var/ucx_meter/cfg/ucx-meter-service start'

If the meter is running you should see a a process "meter.py" running in the background
  Check for it using: ps -ef | grep meter
  
  It should return something like:
    root     26167     1 15 19:52 pts/0    00:00:00 /usr/bin/python /var/ucx_meter/meter.py
    ubuntu   26176 19884  0 19:52 pts/0    00:00:00 grep --color=auto meter

