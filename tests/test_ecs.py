"""Unit tests for ECS service scripts."""
import uuid

import boto3
import pytest
from moto import mock_aws

from services.ecs.create_cluster import create_cluster
from services.ecs.create_service import create_service
from services.ecs.delete_cluster import delete_cluster
from services.ecs.delete_service import delete_service
from services.ecs.deregister_task_definition import deregister_task_definition
from services.ecs.list_clusters import list_clusters
from services.ecs.list_services import list_services
from services.ecs.list_task_definitions import list_task_definitions
from services.ecs.list_tasks import list_tasks
from services.ecs.register_task_definition import register_task_definition
from services.ecs.run_task import run_task
from services.ecs.stop_task import stop_task

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FAMILY = "test-family"
_CONTAINER = "test-container"
_IMAGE = "nginx:latest"


def _register(client, family=_FAMILY):
    """Register a minimal task definition and return the taskDefinition dict."""
    return register_task_definition(client, family, _CONTAINER, _IMAGE)


# ---------------------------------------------------------------------------
# Cluster tests (existing)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Task definition tests
# ---------------------------------------------------------------------------


@mock_aws
def test_register_task_definition():
    client = boto3.client("ecs", region_name="us-east-1")
    task_def = _register(client)
    assert task_def["family"] == _FAMILY
    assert task_def["revision"] >= 1


@mock_aws
def test_list_task_definitions():
    client = boto3.client("ecs", region_name="us-east-1")
    _register(client, "family-alpha")
    _register(client, "family-beta")
    arns = list_task_definitions(client)
    assert len(arns) >= 2


@mock_aws
def test_deregister_task_definition():
    client = boto3.client("ecs", region_name="us-east-1")
    task_def = _register(client)
    td_ref = f"{task_def['family']}:{task_def['revision']}"
    result = deregister_task_definition(client, td_ref)
    assert result["status"] == "INACTIVE"


@mock_aws
def test_deregister_task_definition_dry_run():
    client = boto3.client("ecs", region_name="us-east-1")
    task_def = _register(client)
    td_ref = f"{task_def['family']}:{task_def['revision']}"
    result = deregister_task_definition(client, td_ref, dry_run=True)
    assert result is None


# ---------------------------------------------------------------------------
# Service tests
# ---------------------------------------------------------------------------


@mock_aws
def test_create_service():
    client = boto3.client("ecs", region_name="us-east-1")
    client.create_cluster(clusterName="svc-cluster")
    task_def = _register(client)
    td_ref = f"{task_def['family']}:{task_def['revision']}"
    service = create_service(
        client, "svc-cluster", "my-service", td_ref, desired_count=1
    )
    assert service["serviceName"] == "my-service"
    assert service["desiredCount"] == 1


@mock_aws
def test_list_services():
    client = boto3.client("ecs", region_name="us-east-1")
    client.create_cluster(clusterName="list-svc-cluster")
    task_def = _register(client)
    td_ref = f"{task_def['family']}:{task_def['revision']}"
    client.create_service(
        cluster="list-svc-cluster",
        serviceName="svc-one",
        taskDefinition=td_ref,
        desiredCount=1,
    )
    client.create_service(
        cluster="list-svc-cluster",
        serviceName="svc-two",
        taskDefinition=td_ref,
        desiredCount=1,
    )
    arns = list_services(client, "list-svc-cluster")
    assert len(arns) >= 2


@mock_aws
def test_delete_service():
    client = boto3.client("ecs", region_name="us-east-1")
    client.create_cluster(clusterName="del-svc-cluster")
    task_def = _register(client)
    td_ref = f"{task_def['family']}:{task_def['revision']}"
    client.create_service(
        cluster="del-svc-cluster",
        serviceName="del-svc",
        taskDefinition=td_ref,
        desiredCount=1,
    )
    result = delete_service(client, "del-svc-cluster", "del-svc")
    assert result is not None
    # After deletion the service should be INACTIVE or absent
    desc = client.describe_services(cluster="del-svc-cluster", services=["del-svc"])
    svcs = desc.get("services", [])
    assert not svcs or svcs[0]["status"] == "INACTIVE"


@mock_aws
def test_delete_service_dry_run():
    client = boto3.client("ecs", region_name="us-east-1")
    client.create_cluster(clusterName="dry-svc-cluster")
    task_def = _register(client)
    td_ref = f"{task_def['family']}:{task_def['revision']}"
    client.create_service(
        cluster="dry-svc-cluster",
        serviceName="keep-svc",
        taskDefinition=td_ref,
        desiredCount=1,
    )
    result = delete_service(client, "dry-svc-cluster", "keep-svc", dry_run=True)
    assert result is None
    # Service must still be active
    desc = client.describe_services(cluster="dry-svc-cluster", services=["keep-svc"])
    assert desc["services"][0]["status"] == "ACTIVE"


# ---------------------------------------------------------------------------
# Task run/stop/list tests
# ---------------------------------------------------------------------------


@mock_aws
def test_run_task():
    client = boto3.client("ecs", region_name="us-east-1")
    ec2 = boto3.client("ec2", region_name="us-east-1")
    subnet_id = ec2.describe_subnets()["Subnets"][0]["SubnetId"]
    vpc_id = ec2.describe_subnets()["Subnets"][0]["VpcId"]
    sg = ec2.create_security_group(
        GroupName=f"ecs-sg-{uuid.uuid4().hex[:8]}", Description="test", VpcId=vpc_id
    )
    sg_id = sg["GroupId"]
    client.create_cluster(clusterName="run-cluster")
    task_def = _register(client)
    td_ref = f"{task_def['family']}:{task_def['revision']}"
    net_cfg = {
        "awsvpcConfiguration": {
            "subnets": [subnet_id],
            "securityGroups": [sg_id],
            "assignPublicIp": "ENABLED",
        }
    }
    tasks = run_task(client, "run-cluster", td_ref, launch_type="FARGATE", network_config=net_cfg)
    assert len(tasks) >= 1
    assert "taskArn" in tasks[0]


def _net_cfg(ec2):
    """Return a minimal awsvpcConfiguration dict usable with moto."""
    subnet_id = ec2.describe_subnets()["Subnets"][0]["SubnetId"]
    vpc_id = ec2.describe_subnets()["Subnets"][0]["VpcId"]
    sg_id = ec2.create_security_group(
        GroupName=f"ecs-sg-{uuid.uuid4().hex[:8]}", Description="test", VpcId=vpc_id
    )["GroupId"]
    return {"awsvpcConfiguration": {"subnets": [subnet_id], "securityGroups": [sg_id]}}


@mock_aws
def test_stop_task():
    client = boto3.client("ecs", region_name="us-east-1")
    ec2 = boto3.client("ec2", region_name="us-east-1")
    client.create_cluster(clusterName="stop-cluster")
    task_def = _register(client)
    td_ref = f"{task_def['family']}:{task_def['revision']}"
    tasks = client.run_task(
        cluster="stop-cluster",
        taskDefinition=td_ref,
        launchType="FARGATE",
        networkConfiguration=_net_cfg(ec2),
    )["tasks"]
    task_arn = tasks[0]["taskArn"]
    result = stop_task(client, "stop-cluster", task_arn)
    assert result is not None
    assert result.get("lastStatus") in ("STOPPED", "DEPROVISIONING")


@mock_aws
def test_stop_task_dry_run():
    client = boto3.client("ecs", region_name="us-east-1")
    ec2 = boto3.client("ec2", region_name="us-east-1")
    client.create_cluster(clusterName="dry-stop-cluster")
    task_def = _register(client)
    td_ref = f"{task_def['family']}:{task_def['revision']}"
    tasks = client.run_task(
        cluster="dry-stop-cluster",
        taskDefinition=td_ref,
        launchType="FARGATE",
        networkConfiguration=_net_cfg(ec2),
    )["tasks"]
    task_arn = tasks[0]["taskArn"]
    result = stop_task(client, "dry-stop-cluster", task_arn, dry_run=True)
    assert result is None


@mock_aws
def test_list_tasks():
    client = boto3.client("ecs", region_name="us-east-1")
    ec2 = boto3.client("ec2", region_name="us-east-1")
    client.create_cluster(clusterName="list-tasks-cluster")
    task_def = _register(client)
    td_ref = f"{task_def['family']}:{task_def['revision']}"
    client.run_task(
        cluster="list-tasks-cluster",
        taskDefinition=td_ref,
        launchType="FARGATE",
        networkConfiguration=_net_cfg(ec2),
    )
    arns = list_tasks(client, "list-tasks-cluster", desired_status="RUNNING")
    assert len(arns) >= 1

