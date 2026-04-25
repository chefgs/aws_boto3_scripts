"""List ECR repositories."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_repositories(client):
    """Return a list of ECR repository dicts."""
    try:
        paginator = client.get_paginator("describe_repositories")
        repos = []
        for page in paginator.paginate():
            repos.extend(page.get("repositories", []))
        for repo in repos:
            logger.info("Repository: %s (%s)", repo["repositoryName"], repo["repositoryUri"])
        return repos
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list repositories: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List ECR repositories")
    args = parser.parse_args()
    client = get_client("ecr", args.profile, args.region)
    list_repositories(client)
