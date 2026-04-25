"""Describe an ECR repository."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def describe_repository(client, name):
    """Return the description dict for an ECR repository."""
    try:
        response = client.describe_repositories(repositoryNames=[name])
        repos = response.get("repositories", [])
        if not repos:
            logger.warning("Repository not found: %s", name)
            return None
        repo = repos[0]
        logger.info("Repository %s: %s", name, repo)
        return repo
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to describe repository %s: %s", name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Describe an ECR repository")
    parser.add_argument("--name", required=True, help="Repository name")
    args = parser.parse_args()
    client = get_client("ecr", args.profile, args.region)
    describe_repository(client, args.name)
