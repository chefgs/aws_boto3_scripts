"""Unit tests for ECS service scripts."""
import boto3
import pytest
from moto import mock_aws

from services.ecs.create_cluster import create_cluster
from services.ecs.delete_cluster import delete_cluster
from services.ecs.list_clusters import list_clusters


@mock_aws
def test_create_cluster():
    client = boto3.client("ecs", region_name="us-east-1")
    response = create_cluster(client, "test-cluster")
    assert response["cluster"]["clusterName"] == "test-cluster"


@mock_aws
def test_list_clusters():
    client = boto3.client("ecs", region_name="us-east-1")
    client.create_cluster(clusterName="cluster-a")
    client.create_cluster(clusterName="cluster-b")
    arns = list_clusters(client)
    assert len(arns) >= 2


@mock_aws
def test_delete_cluster():
    client = boto3.client("ecs", region_name="us-east-1")
    client.create_cluster(clusterName="delete-me")
    delete_cluster(client, "delete-me")
    # moto keeps INACTIVE clusters in list_clusters; verify status instead
    desc = client.describe_clusters(clusters=["delete-me"])["clusters"]
    assert not desc or desc[0]["status"] == "INACTIVE"


@mock_aws
def test_delete_cluster_dry_run():
    client = boto3.client("ecs", region_name="us-east-1")
    client.create_cluster(clusterName="dry-run-cluster")
    result = delete_cluster(client, "dry-run-cluster", dry_run=True)
    assert result is None
