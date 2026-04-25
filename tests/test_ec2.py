"""Unit tests for EC2 service scripts."""
import boto3
import pytest
from moto import mock_aws

from services.ec2.create_instance import create_instance
from services.ec2.delete_instance import delete_instance
from services.ec2.list_instances import list_instances


@mock_aws
def test_create_instance():
    client = boto3.client("ec2", region_name="us-east-1")
    ids = create_instance(client, "ami-12345678", "t2.micro", "my-key")
    assert len(ids) == 1
    assert ids[0].startswith("i-")


@mock_aws
def test_list_instances():
    client = boto3.client("ec2", region_name="us-east-1")
    client.run_instances(ImageId="ami-12345678", MinCount=2, MaxCount=2)
    instances = list_instances(client)
    assert len(instances) >= 2


@mock_aws
def test_delete_instance():
    client = boto3.client("ec2", region_name="us-east-1")
    resp = client.run_instances(ImageId="ami-12345678", MinCount=1, MaxCount=1)
    instance_id = resp["Instances"][0]["InstanceId"]
    delete_instance(client, instance_id)
    instances = list_instances(client, state="terminated")
    ids = [i["InstanceId"] for i in instances]
    assert instance_id in ids


@mock_aws
def test_delete_instance_dry_run():
    client = boto3.client("ec2", region_name="us-east-1")
    resp = client.run_instances(ImageId="ami-12345678", MinCount=1, MaxCount=1)
    instance_id = resp["Instances"][0]["InstanceId"]
    result = delete_instance(client, instance_id, dry_run=True)
    assert result is None
