import os
import boto3
from dotenv import load_dotenv

load_dotenv()
ec2 = boto3.client(
    "ec2",
    endpoint_url=os.getenv("AWS_ENDPOINT"),
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test",
)


def by_name(name):
    r = ec2.describe_instances(Filters=[
        {"Name": "tag:Name", "Values": [name]},
        {"Name": "instance-state-name", "Values": ["pending", "running", "stopped"]},
    ])
    return r["Reservations"][0]["Instances"][0]["InstanceId"]


ec2.create_tags(Resources=[by_name("web-01")], Tags=[{"Key": "owner", "Value": "ravi"}])
ec2.stop_instances(InstanceIds=[by_name("db-01")])
ec2.terminate_instances(InstanceIds=[by_name("web-02")])
print("web-01 owner changed, db-01 stopped, web-02 terminated")