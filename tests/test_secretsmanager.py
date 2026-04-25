"""Unit tests for Secrets Manager service scripts."""
import boto3
import pytest
from moto import mock_aws

from services.secretsmanager.create_secret import create_secret
from services.secretsmanager.delete_secret import delete_secret
from services.secretsmanager.get_secret import get_secret
from services.secretsmanager.list_secrets import list_secrets


@mock_aws
def test_create_secret():
    client = boto3.client("secretsmanager", region_name="us-east-1")
    arn = create_secret(client, "my-secret", "super-secret-value")
    assert arn is not None


@mock_aws
def test_get_secret():
    client = boto3.client("secretsmanager", region_name="us-east-1")
    client.create_secret(Name="get-me", SecretString="my-value")
    value = get_secret(client, "get-me")
    assert value == "my-value"


@mock_aws
def test_list_secrets():
    client = boto3.client("secretsmanager", region_name="us-east-1")
    client.create_secret(Name="secret-1", SecretString="v1")
    client.create_secret(Name="secret-2", SecretString="v2")
    secrets = list_secrets(client)
    assert len(secrets) >= 2


@mock_aws
def test_delete_secret():
    client = boto3.client("secretsmanager", region_name="us-east-1")
    client.create_secret(Name="del-secret", SecretString="val")
    delete_secret(client, "del-secret")
    secrets = list_secrets(client)
    names = [s["Name"] for s in secrets]
    assert "del-secret" not in names


@mock_aws
def test_delete_secret_dry_run():
    client = boto3.client("secretsmanager", region_name="us-east-1")
    client.create_secret(Name="dry-secret", SecretString="val")
    result = delete_secret(client, "dry-secret", dry_run=True)
    assert result is None
    secrets = list_secrets(client)
    names = [s["Name"] for s in secrets]
    assert "dry-secret" in names
