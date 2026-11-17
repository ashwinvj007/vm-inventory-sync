import os
import boto3
from models import VM
from collectors.base import Collector

SIZES = {  # instance type -> (cpu, ram_mb)
    "t2.micro": (1, 1024),
    "t2.small": (1, 2048),
    "t3.medium": (2, 4096),
}

class AwsCollector(Collector):
    name = "aws"

    def __init__(self):
        self.ec2 = boto3.client(
            "ec2",
            endpoint_url=os.getenv("AWS_ENDPOINT"),
            region_name="us-east-1",
            aws_access_key_id="test",
            aws_secret_access_key="test",
        )

    def collect(self) -> list[VM]:
        vms = []
        for page in self.ec2.get_paginator("describe_instances").paginate():
            for res in page["Reservations"]:
                for i in res["Instances"]:
                    state = i["State"]["Name"]
                    if state in ("terminated", "shutting-down"):
                        continue
                    tags = {t["Key"]: t["Value"] for t in i.get("Tags", [])}
                    cpu, ram = SIZES.get(i["InstanceType"], (1, 1024))
                    ips = [i[k] for k in ("PrivateIpAddress", "PublicIpAddress") if i.get(k)]
                    vms.append(VM(
                        source="aws",
                        external_id=i["InstanceId"],
                        hostname=tags.get("Name", i["InstanceId"]),
                        ips=ips,
                        os=i.get("PlatformDetails", "Linux/UNIX"),
                        cpu=cpu,
                        ram_mb=ram,
                        disk_gb=8,
                        tags=tags,
                        owner=tags.get("owner", ""),
                        power_state="on" if state == "running" else "off",
                        location=i["Placement"]["AvailabilityZone"],
                    ))
        return vms