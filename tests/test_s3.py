"""Unit tests for S3 service scripts."""
import boto3
import pytest
from moto import mock_aws

from services.s3.create_bucket import create_bucket
from services.s3.delete_bucket import delete_bucket
from services.s3.list_buckets import list_buckets


@mock_aws
def test_create_bucket():
    client = boto3.client("s3", region_name="us-east-1")
    create_bucket(client, "test-bucket-create", "us-east-1")
    response = client.list_buckets()
    names = [b["Name"] for b in response["Buckets"]]
    assert "test-bucket-create" in names


@mock_aws
def test_list_buckets():
    client = boto3.client("s3", region_name="us-east-1")
    client.create_bucket(Bucket="list-bucket-1")
    client.create_bucket(Bucket="list-bucket-2")
    buckets = list_buckets(client)
    assert "list-bucket-1" in buckets
    assert "list-bucket-2" in buckets


@mock_aws
def test_delete_bucket():
    client = boto3.client("s3", region_name="us-east-1")
    client.create_bucket(Bucket="bucket-to-delete")
    delete_bucket(client, "bucket-to-delete")
    response = client.list_buckets()
    names = [b["Name"] for b in response["Buckets"]]
    assert "bucket-to-delete" not in names


@mock_aws
def test_delete_bucket_dry_run():
    client = boto3.client("s3", region_name="us-east-1")
    client.create_bucket(Bucket="bucket-dry-run")
    result = delete_bucket(client, "bucket-dry-run", dry_run=True)
    assert result is None
    # Bucket should still exist
    response = client.list_buckets()
    names = [b["Name"] for b in response["Buckets"]]
    assert "bucket-dry-run" in names
