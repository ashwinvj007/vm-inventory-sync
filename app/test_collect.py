from dotenv import load_dotenv
load_dotenv()
from collectors.aws import AwsCollector
from collectors.azure import AzureCollector
from collectors.vmware import VmwareCollector

total = 0
for c in (AwsCollector(), AzureCollector(), VmwareCollector()):
    vms = c.collect()
    total += len(vms)
    print(c.name, len(vms))
print("total", total)