import psutil
import urllib2
#import platform
#import cpu-info

auth_uri="https://api.6fusion.com:443/api/v2/"


class organization(object):
    def __init__(self):
        self.create_inf_uri="organizations"
        self.oauth_token="30a62bf3a34104c882eaa47655e99fa6b81ea1fd3428fa5f5e43b74b4b0a7729"
        self.org_id=4196
        self.infr_id=0

    def check_infr_exist(self,infr_name):
        return 0

    def create_infr(self,infr_name):
        if self.check_infr_exist(""):
            print "Infrastructure exists. Moving onto adding machine."
        else:
            try:
                auth_req = urllib2.Request(auth_uri + self.create_inf_uri)
                auth_req.add_header('id',"")
                auth_req.add_header('infrastructure',"")
                auth_req.add_header('organization_id',"")
                response = urllib2.urlopen(auth_req)
                token = response.info()
                print token
                i=0
            except Exception as e:
                print 'ERROR: ' + str(e)
                print 'ERROR: ' + str(e)
                raise Exception('Infrastructure creation failed.  Halting execution')

class machine(object):
    def __init__(self):
        self.create_machine_uri=""

    def machine_exist(self,id):
        return 0

    def create_machine(self,org_id):
        uuid=self.create_uuid_for_machine_name()
        print uuid
        if self.machine_exist(uuid):
            print "Machine exists. Moving onto add measurements/readings."
        else:
            try:
                auth_req = urllib2.Request(auth_uri + self.create_machine_uri)
                auth_req.add_header('id',"")
                auth_req.add_header('infrastructure',"")
                auth_req.add_header('organization_id',"")
                response = urllib2.urlopen(auth_req)
                token = response.info()
                print token
                i=0
            except Exception as e:
                print 'ERROR: ' + str(e)
                raise Exception('Infrastructure creation failed.  Halting execution')

    def create_uuid_for_machine_name(self):
        return "fdkjfkdjfd"  # combo of base64 for company name, "-", machine identifier - mac perhaps

class readings(object):
    def __init__(self):
        self.send_metrics_api_url="measurements"
        self.cpu=0
        self.mem=0
        self.network=0
        self.disk_pctg=0
        self.disk_amt=0
        self.disk_io=0

    def gather_metrics(self):
        self.cpu=self.get_cpu()
        self.mem=self.get_memory()
        self.disk_io=self.get_disk_io()
        self.disk_pctg=self.get_disk_percentage()
        self.network=self.network_io()
        self.send_metrics()

    def get_cpu(self):
        return psutil.cpu_percent()

    def get_memory(self):
        return psutil.virtual_memory()

    def get_disk_io(self):
        print("")

    def get_disk_percentage(self):
        print("")

    def network_io(self):
        print("")

    def send_metrics(self):
        try:
            auth_req = urllib2.Request(auth_uri + send_metrics_api_url)
            auth_req.add_header('id',"")
            auth_req.add_header('infrastructure',"")
            auth_req.add_header('organization_id',"")
            response = urllib2.urlopen(auth_req)
            token = response.info()
            print token
            i=0
        except Exception as e:
            print 'ERROR: ' + str(e)
            raise Exception('Measurement upload failed.  Halting execution')

def main():
    org=organization()
    node=machine()

    print org.org_id
    org_id=org.create_infr("temp")

    node.create_machine(org_id)

    meter=readings()
    print meter.get_memory()

    meter.gather_metrics()

if __name__ == "__main__":
    main()





# try {Clear-Host;
# Write-Host "----------------------------------------------------------";
# Write-Host "| Welcome to 6fusion VMware Data Collection Tool |";
# Write-Host "----------------------------------------------------------";
# Add-PSSnapin VMware.VimAutomation.Core -ErrorAction SilentlyContinue;
# $Server = Read-Host " vCenter Server ";
# $Username = Read-Host " Username ";
# $Password = Read-Host -assecurestring " Password ";
# $Directory = Read-Host " Directory Name ";
# $scriptPath = split-path -parent $MyInvocation.MyCommand.Definition;
# $credentials = New-Object System.Management.Automation.PSCredential ($Username, $Password);
# $FileLocation = ($scriptPath) + "\" + ($Directory);
# Write-Host "";
# Write-Host ""(Get-Date) ": Starting Data Collection...";
# Write-Host ""(Get-Date) ": Connecting to vCenter Server..." -NoNewLine;
# $Session = Connect-VIServer -Server $Server -Protocol https -Credential $credentials -ErrorAction Stop;
# Write-Host "Success." -foregroundColor Green;
# Write-Host ""(Get-Date) ": Creating directory to store files ..." -NoNewLine;
# If (!(Test-Path $FileLocation)){New-Item -Path $FileLocation -ItemType Directory | Out-Null;}else{Throw "This directory already exists, please rerun using a directory name that is not already taken."};
# Write-Host "Success." -foregroundColor Green;
# Write-Host ""(Get-Date) ": Exporting list of hosts..." -NoNewLine;
# Get-VMHost | Select-Object Name,ConnectionState,PowerState,NumCpu,CpuTotalMhz,CpuUsageMhz,MemoryTotalMB,MemoryUsageMB,ProcessorType | Export-Csv (($FileLocation) + "\hosts.csv") -NoTypeInformation;
# Write-Host "Complete." -foregroundColor Green;
# Write-Host ""(Get-Date) ": Exporting list of datastores..." -NoNewLine;
# Get-Datastore | Select-Object Name,Type,State,CapacityGB,FreeSpaceGB | Export-Csv (($FileLocation) + "\datastores.csv") -NoTypeInformation;
# Write-Host "Complete." -foregroundColor Green;
# Write-Host ""(Get-Date) ": Exporting list of virtual machines..." -NoNewLine;
# $VMs = Get-VM;
# $VMs | Select-Object PersistentId,Id,Name,PowerState,NumCpu,MemoryMB,UsedSpaceGB,ProvisionedSpaceGB,VMHost,Directory | Export-Csv (($FileLocation) + "\machines.csv") -NoTypeInformation;
# Write-Host "Complete." -foregroundColor Green;
# $VMsWithStats = 0;
# $VMsWithoutStats = 0;
# ForEach ($VM in $VMs){Write-Host ""(Get-Date) ": Exporting performance data for" $VM "..." -NoNewLine;
# $Stats = Get-StatType -Entity $VM -Interval "Past Month";
# if (!$Stats) {$VMsWithoutStats++;Write-Host "No performance metrics found..." -NoNewLine;}else {Get-Stat -Entity $VM -Stat $Stats -IntervalSecs 7200 | Select-Object EntityId,Entity,Instance,Timestamp,MetricId,Value,Unit| Export-Csv (($FileLocation) + "\" + ($VM) + ".csv") -NoTypeInformation;$VMsWithStats++;};Write-Host "Complete." -foregroundColor Green;};Write-Host ""(Get-Date) ": Compressing files ..." -NoNewLine;$CompressedFileName = (($FileLocation) + ".zip");set-content $CompressedFileName ("PK" + [char]5 + [char]6 + ("$([char]0)" * 18));$FileCompressor = New-Object -ComObject Shell.Application;$FileCompressor.namespace($CompressedFileName).Copyhere($FileCompressor.namespace($FileLocation).Items());$Folder = Get-Item $FileLocation;While ($FileCompressor.namespace($CompressedFileName).Items().Count -ne $Folder.GetFiles().Count) {Write-Host "." -NoNewLine};Write-Host "Complete." -foregroundColor Green;Write-Host ""(Get-Date) ": Generating MD5 hash ..." -NoNewLine;$MD5 = New-Object -TypeName System.Security.Cryptography.MD5CryptoServiceProvider;$Hash = [System.BitConverter]::ToString($MD5.ComputeHash([System.IO.File]::ReadAllBytes($CompressedFileName)));Write-Host "Complete." -foregroundColor Green;Write-Host ""(Get-Date) ": Renaming compressed file ..." -NoNewLine;$NewCompressedFileName = ($Hash -replace "-") + "-" + ((Get-Item $CompressedFileName).Name);Rename-Item -Path $CompressedFileName -NewName $NewCompressedFileName;Write-Host "Complete." -foregroundColor Green;Write-Host ""(Get-Date) ": Completed Data Collection.";Write-Host "";Write-Host "";Write-Host "----------------------------------------------------------";Write-Host "| VMware Data Collection Summary |";Write-Host "----------------------------------------------------------";Write-Host " Upload File: " ($NewCompressedFileName);Write-Host " Total Machines: " ($VMs.count);Write-Host " Machines with Readings: " ($VMsWithStats);Write-Host " Machines without Readings: " ($VMsWithoutStats);Write-Host "";Write-Host "";}catch {Write-Host "Failed" -foregroundColor Red;Write-Host "";Write-Host "The following error occured: " -foregroundColor Red;Write-Host $_.Exception.Message -foregroundColor Red;Write-Host "";Write-Host ""(Get-Date) ": Completed Data Collection with errors.";} finally {if ($Session){Disconnect-VIServer -Server $Session -Confirm:$false;}};