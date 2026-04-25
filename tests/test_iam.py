"""Unit tests for IAM service scripts."""
import boto3
import pytest
from moto import mock_aws

from services.iam.create_user import create_user
from services.iam.delete_user import delete_user
from services.iam.list_users import list_users
from services.iam.create_role import create_role
from services.iam.list_roles import list_roles
from services.iam.attach_policy import attach_policy


@mock_aws
def test_create_user():
    client = boto3.client("iam", region_name="us-east-1")
    user = create_user(client, "testuser")
    assert user["UserName"] == "testuser"


@mock_aws
def test_list_users():
    client = boto3.client("iam", region_name="us-east-1")
    client.create_user(UserName="user1")
    client.create_user(UserName="user2")
    users = list_users(client)
    names = [u["UserName"] for u in users]
    assert "user1" in names
    assert "user2" in names


@mock_aws
def test_delete_user():
    client = boto3.client("iam", region_name="us-east-1")
    client.create_user(UserName="to-delete")
    delete_user(client, "to-delete")
    users = list_users(client)
    names = [u["UserName"] for u in users]
    assert "to-delete" not in names


@mock_aws
def test_delete_user_dry_run():
    client = boto3.client("iam", region_name="us-east-1")
    client.create_user(UserName="dry-run-user")
    result = delete_user(client, "dry-run-user", dry_run=True)
    assert result is None
    users = list_users(client)
    names = [u["UserName"] for u in users]
    assert "dry-run-user" in names


@mock_aws
def test_create_role():
    client = boto3.client("iam", region_name="us-east-1")
    role = create_role(client, "test-role", "ec2.amazonaws.com")
    assert role["RoleName"] == "test-role"


@mock_aws
def test_list_roles():
    client = boto3.client("iam", region_name="us-east-1")
    import json
    trust = json.dumps({"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"}, "Action": "sts:AssumeRole"}]})
    client.create_role(RoleName="role1", AssumeRolePolicyDocument=trust)
    roles = list_roles(client)
    names = [r["RoleName"] for r in roles]
    assert "role1" in names


@mock_aws
def test_attach_policy_to_user():
    client = boto3.client("iam", region_name="us-east-1")
    client.create_user(UserName="policy-user")
    # Create a local managed policy (moto doesn't auto-create AWS managed policies)
    policy_arn = client.create_policy(
        PolicyName="TestReadOnly",
        PolicyDocument='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"s3:Get*","Resource":"*"}]}',
    )["Policy"]["Arn"]
    attach_policy(client, "user", "policy-user", policy_arn)
    attached = client.list_attached_user_policies(UserName="policy-user")["AttachedPolicies"]
    arns = [p["PolicyArn"] for p in attached]
    assert policy_arn in arns
