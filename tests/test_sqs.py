"""Unit tests for SQS service scripts."""
import boto3
import pytest
from moto import mock_aws

from services.sqs.create_queue import create_queue
from services.sqs.delete_queue import delete_queue
from services.sqs.list_queues import list_queues
from services.sqs.receive_messages import receive_messages
from services.sqs.send_message import send_message


@mock_aws
def test_create_queue():
    client = boto3.client("sqs", region_name="us-east-1")
    url = create_queue(client, "test-queue")
    assert "test-queue" in url


@mock_aws
def test_list_queues():
    client = boto3.client("sqs", region_name="us-east-1")
    client.create_queue(QueueName="queue-a")
    client.create_queue(QueueName="queue-b")
    urls = list_queues(client)
    assert any("queue-a" in u for u in urls)
    assert any("queue-b" in u for u in urls)


@mock_aws
def test_send_and_receive():
    client = boto3.client("sqs", region_name="us-east-1")
    url = client.create_queue(QueueName="msg-queue")["QueueUrl"]
    send_message(client, url, "hello world")
    messages = receive_messages(client, url)
    assert len(messages) == 1
    assert messages[0]["Body"] == "hello world"


@mock_aws
def test_delete_queue():
    client = boto3.client("sqs", region_name="us-east-1")
    url = client.create_queue(QueueName="del-queue")["QueueUrl"]
    delete_queue(client, url)
    urls = list_queues(client)
    assert not any("del-queue" in u for u in urls)


@mock_aws
def test_delete_queue_dry_run():
    client = boto3.client("sqs", region_name="us-east-1")
    url = client.create_queue(QueueName="dry-queue")["QueueUrl"]
    result = delete_queue(client, url, dry_run=True)
    assert result is None
    urls = list_queues(client)
    assert any("dry-queue" in u for u in urls)
