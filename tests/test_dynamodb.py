"""Unit tests for DynamoDB service scripts."""
import boto3
import pytest
from moto import mock_aws

from services.dynamodb.create_table import create_table
from services.dynamodb.delete_table import delete_table
from services.dynamodb.get_item import get_item
from services.dynamodb.list_tables import list_tables
from services.dynamodb.put_item import put_item


@mock_aws
def test_create_table():
    client = boto3.client("dynamodb", region_name="us-east-1")
    desc = create_table(client, "test-table", "id")
    assert desc["TableName"] == "test-table"


@mock_aws
def test_create_table_with_sort_key():
    client = boto3.client("dynamodb", region_name="us-east-1")
    desc = create_table(client, "sort-table", "pk", "sk")
    assert desc["TableName"] == "sort-table"


@mock_aws
def test_list_tables():
    client = boto3.client("dynamodb", region_name="us-east-1")
    client.create_table(
        TableName="table1",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    tables = list_tables(client)
    assert "table1" in tables


@mock_aws
def test_put_and_get_item():
    client = boto3.client("dynamodb", region_name="us-east-1")
    create_table(client, "items-table", "id")
    put_item(client, "items-table", {"id": {"S": "42"}, "name": {"S": "test"}})
    item = get_item(client, "items-table", {"id": {"S": "42"}})
    assert item["name"]["S"] == "test"


@mock_aws
def test_delete_table():
    client = boto3.client("dynamodb", region_name="us-east-1")
    create_table(client, "del-table", "id")
    delete_table(client, "del-table")
    tables = list_tables(client)
    assert "del-table" not in tables


@mock_aws
def test_delete_table_dry_run():
    client = boto3.client("dynamodb", region_name="us-east-1")
    create_table(client, "dry-table", "id")
    result = delete_table(client, "dry-table", dry_run=True)
    assert result is None
    tables = list_tables(client)
    assert "dry-table" in tables
