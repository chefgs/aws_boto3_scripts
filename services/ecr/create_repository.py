"""Create an ECR repository."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_repository(client, name):
    """Create an ECR repository and return the repository data."""
    try:
        response = client.create_repository(repositoryName=name)
        repo = response["repository"]
        uri = repo["repositoryUri"]
        logger.info("Created ECR repository: %s (%s)", name, uri)
        return repo
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create repository %s: %s", name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create an ECR repository")
    parser.add_argument("--name", required=True, help="Repository name")
    args = parser.parse_args()
    client = get_client("ecr", args.profile, args.region)
    create_repository(client, args.name)
