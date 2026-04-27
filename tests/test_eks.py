"""Unit tests for EKS service scripts."""
import boto3
import pytest
from moto import mock_aws

from services.eks.create_cluster import create_cluster
from services.eks.delete_cluster import delete_cluster
from services.eks.describe_cluster import describe_cluster
from services.eks.list_clusters import list_clusters

# Minimal VPC config accepted by moto
_VPC_CONFIG = {"subnetIds": ["subnet-12345678"]}
_ROLE_ARN = "arn:aws:iam::123456789012:role/eks-role"


@mock_aws
def test_create_cluster():
    client = boto3.client("eks", region_name="us-east-1")
    cluster = create_cluster(client, "test-cluster", _ROLE_ARN, _VPC_CONFIG)
    assert cluster["name"] == "test-cluster"
    assert "arn" in cluster


@mock_aws
def test_list_clusters():
    client = boto3.client("eks", region_name="us-east-1")
    client.create_cluster(
        name="cluster-a",
        version="1.29",
        roleArn=_ROLE_ARN,
        resourcesVpcConfig=_VPC_CONFIG,
    )
    client.create_cluster(
        name="cluster-b",
        version="1.29",
        roleArn=_ROLE_ARN,
        resourcesVpcConfig=_VPC_CONFIG,
    )
    names = list_clusters(client)
    assert "cluster-a" in names
    assert "cluster-b" in names
    assert len(names) >= 2


@mock_aws
def test_describe_cluster():
    client = boto3.client("eks", region_name="us-east-1")
    client.create_cluster(
        name="describe-me",
        version="1.29",
        roleArn=_ROLE_ARN,
        resourcesVpcConfig=_VPC_CONFIG,
    )
    cluster = describe_cluster(client, "describe-me")
    assert cluster is not None
    assert cluster["name"] == "describe-me"
    assert cluster["status"] in ("ACTIVE", "CREATING")


@mock_aws
def test_delete_cluster():
    client = boto3.client("eks", region_name="us-east-1")
    client.create_cluster(
        name="delete-me",
        version="1.29",
        roleArn=_ROLE_ARN,
        resourcesVpcConfig=_VPC_CONFIG,
    )
    result = delete_cluster(client, "delete-me")
    assert result is not None
    names = list_clusters(client)
    assert "delete-me" not in names


@mock_aws
def test_delete_cluster_dry_run():
    client = boto3.client("eks", region_name="us-east-1")
    client.create_cluster(
        name="keep-me",
        version="1.29",
        roleArn=_ROLE_ARN,
        resourcesVpcConfig=_VPC_CONFIG,
    )
    result = delete_cluster(client, "keep-me", dry_run=True)
    assert result is None
    # Cluster must still exist
    names = list_clusters(client)
    assert "keep-me" in names
