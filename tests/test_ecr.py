"""Unit tests for ECR service scripts."""
import boto3
import pytest
from moto import mock_aws

from services.ecr.create_repository import create_repository
from services.ecr.delete_repository import delete_repository
from services.ecr.describe_repository import describe_repository
from services.ecr.list_repositories import list_repositories


@mock_aws
def test_create_repository():
    client = boto3.client("ecr", region_name="us-east-1")
    repo = create_repository(client, "my-app")
    assert repo["repositoryName"] == "my-app"
    assert "repositoryUri" in repo


@mock_aws
def test_list_repositories():
    client = boto3.client("ecr", region_name="us-east-1")
    client.create_repository(repositoryName="repo-a")
    client.create_repository(repositoryName="repo-b")
    repos = list_repositories(client)
    names = [r["repositoryName"] for r in repos]
    assert "repo-a" in names
    assert "repo-b" in names
    assert len(repos) >= 2


@mock_aws
def test_describe_repository():
    client = boto3.client("ecr", region_name="us-east-1")
    client.create_repository(repositoryName="describe-me")
    repo = describe_repository(client, "describe-me")
    assert repo is not None
    assert repo["repositoryName"] == "describe-me"


@mock_aws
def test_delete_repository():
    client = boto3.client("ecr", region_name="us-east-1")
    client.create_repository(repositoryName="delete-me")
    delete_repository(client, "delete-me")
    resp = client.describe_repositories()
    names = [r["repositoryName"] for r in resp.get("repositories", [])]
    assert "delete-me" not in names


@mock_aws
def test_delete_repository_dry_run():
    client = boto3.client("ecr", region_name="us-east-1")
    client.create_repository(repositoryName="keep-me")
    result = delete_repository(client, "keep-me", dry_run=True)
    assert result is None
    # Repository must still exist
    resp = client.describe_repositories(repositoryNames=["keep-me"])
    assert len(resp["repositories"]) == 1
