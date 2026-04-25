"""Shared boto3 session and client helpers."""
import boto3
import logging

logger = logging.getLogger(__name__)


def get_session(profile=None, region="us-east-1"):
    """Create a boto3 session with an optional profile and region."""
    kwargs = {"region_name": region}
    if profile:
        kwargs["profile_name"] = profile
    return boto3.Session(**kwargs)


def get_client(service, profile=None, region="us-east-1"):
    """Return a boto3 client for the given service."""
    session = get_session(profile, region)
    return session.client(service)


def get_resource(service, profile=None, region="us-east-1"):
    """Return a boto3 resource for the given service."""
    session = get_session(profile, region)
    return session.resource(service)


def get_account_id(profile=None, region="us-east-1"):
    """Return the AWS account ID for the given credentials/profile."""
    client = get_client("sts", profile, region)
    return client.get_caller_identity()["Account"]
