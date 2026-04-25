"""Unit tests for SSM Parameter Store service scripts."""
import boto3
import pytest
from moto import mock_aws

from services.ssm.delete_parameter import delete_parameter
from services.ssm.get_parameter import get_parameter
from services.ssm.list_parameters import list_parameters
from services.ssm.put_parameter import put_parameter


@mock_aws
def test_put_parameter():
    client = boto3.client("ssm", region_name="us-east-1")
    response = put_parameter(client, "/myapp/key", "myvalue")
    assert response["Version"] >= 1


@mock_aws
def test_get_parameter():
    client = boto3.client("ssm", region_name="us-east-1")
    client.put_parameter(Name="/myapp/key", Value="hello", Type="String")
    value = get_parameter(client, "/myapp/key")
    assert value == "hello"


@mock_aws
def test_list_parameters():
    client = boto3.client("ssm", region_name="us-east-1")
    client.put_parameter(Name="/app/param1", Value="v1", Type="String")
    client.put_parameter(Name="/app/param2", Value="v2", Type="String")
    params = list_parameters(client)
    names = [p["Name"] for p in params]
    assert "/app/param1" in names
    assert "/app/param2" in names


@mock_aws
def test_list_parameters_by_path():
    client = boto3.client("ssm", region_name="us-east-1")
    client.put_parameter(Name="/prod/db/password", Value="secret", Type="String")
    params = list_parameters(client, path="/prod")
    names = [p["Name"] for p in params]
    assert "/prod/db/password" in names


@mock_aws
def test_delete_parameter():
    client = boto3.client("ssm", region_name="us-east-1")
    client.put_parameter(Name="/del/param", Value="val", Type="String")
    delete_parameter(client, "/del/param")
    params = list_parameters(client)
    names = [p["Name"] for p in params]
    assert "/del/param" not in names


@mock_aws
def test_delete_parameter_dry_run():
    client = boto3.client("ssm", region_name="us-east-1")
    client.put_parameter(Name="/dry/param", Value="val", Type="String")
    result = delete_parameter(client, "/dry/param", dry_run=True)
    assert result is None
    params = list_parameters(client)
    names = [p["Name"] for p in params]
    assert "/dry/param" in names
