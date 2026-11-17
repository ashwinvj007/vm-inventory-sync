import os
import boto3
from dotenv import load_dotenv

load_dotenv()
ec2 = boto3.client(
    "ec2",
    endpoint_url=os.getenv("AWS_ENDPOINT", "http://localhost:5000"),
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test",
)

existing = ec2.describe_instances(
    Filters=[{"Name": "instance-state-name", "Values": ["pending", "running", "stopped"]}]
)
if any(r["Instances"] for r in existing["Reservations"]):
    print("Instances already exist, skipping seed")
    raise SystemExit

VMS = [
    ("web-01", "t2.micro", "ashwin"),
    ("web-02", "t2.micro", "ashwin"),
    ("db-01", "t3.medium", "priya"),
    ("app-01", "t2.small", "priya"),
    ("batch-01", "t3.medium", "ravi"),
]
for name, itype, owner in VMS:
    ec2.run_instances(
        ImageId="ami-12345678", InstanceType=itype, MinCount=1, MaxCount=1,
        TagSpecifications=[{"ResourceType": "instance", "Tags": [
            {"Key": "Name", "Value": name},
            {"Key": "owner", "Value": owner},
            {"Key": "env", "Value": "demo"},
        ]}],
    )
    print("created", name)