"""Unit tests for KMS service scripts."""
import boto3
import pytest
from moto import mock_aws

from services.kms.create_key import create_key
from services.kms.delete_key import delete_key
from services.kms.list_keys import list_keys


@mock_aws
def test_create_key():
    client = boto3.client("kms", region_name="us-east-1")
    metadata = create_key(client, "test key")
    assert "KeyId" in metadata


@mock_aws
def test_list_keys():
    client = boto3.client("kms", region_name="us-east-1")
    client.create_key(Description="key1")
    client.create_key(Description="key2")
    keys = list_keys(client)
    assert len(keys) >= 2


@mock_aws
def test_delete_key():
    client = boto3.client("kms", region_name="us-east-1")
    key = client.create_key(Description="to-delete")
    key_id = key["KeyMetadata"]["KeyId"]
    response = delete_key(client, key_id, pending_days=7)
    assert response["KeyId"] == key_id


@mock_aws
def test_delete_key_dry_run():
    client = boto3.client("kms", region_name="us-east-1")
    key = client.create_key(Description="dry-run-key")
    key_id = key["KeyMetadata"]["KeyId"]
    result = delete_key(client, key_id, dry_run=True)
    assert result is None
