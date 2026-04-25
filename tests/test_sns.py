"""Unit tests for SNS service scripts."""
import boto3
import pytest
from moto import mock_aws

from services.sns.create_topic import create_topic
from services.sns.delete_topic import delete_topic
from services.sns.list_topics import list_topics
from services.sns.publish_message import publish_message
from services.sns.subscribe import subscribe


@mock_aws
def test_create_topic():
    client = boto3.client("sns", region_name="us-east-1")
    arn = create_topic(client, "test-topic")
    assert "test-topic" in arn


@mock_aws
def test_list_topics():
    client = boto3.client("sns", region_name="us-east-1")
    client.create_topic(Name="topic-a")
    client.create_topic(Name="topic-b")
    arns = list_topics(client)
    assert any("topic-a" in a for a in arns)
    assert any("topic-b" in a for a in arns)


@mock_aws
def test_publish_message():
    client = boto3.client("sns", region_name="us-east-1")
    arn = client.create_topic(Name="pub-topic")["TopicArn"]
    msg_id = publish_message(client, arn, "test message")
    assert msg_id is not None


@mock_aws
def test_subscribe():
    client = boto3.client("sns", region_name="us-east-1")
    arn = client.create_topic(Name="sub-topic")["TopicArn"]
    sub_arn = subscribe(client, arn, "sqs", "arn:aws:sqs:us-east-1:123456789012:my-queue")
    assert sub_arn is not None


@mock_aws
def test_delete_topic():
    client = boto3.client("sns", region_name="us-east-1")
    arn = client.create_topic(Name="del-topic")["TopicArn"]
    delete_topic(client, arn)
    arns = list_topics(client)
    assert not any("del-topic" in a for a in arns)


@mock_aws
def test_delete_topic_dry_run():
    client = boto3.client("sns", region_name="us-east-1")
    arn = client.create_topic(Name="dry-topic")["TopicArn"]
    result = delete_topic(client, arn, dry_run=True)
    assert result is None
    arns = list_topics(client)
    assert any("dry-topic" in a for a in arns)
