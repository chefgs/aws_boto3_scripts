"""Delete an ECR repository."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_repository(client, name, force=True, dry_run=False):
    """Delete an ECR repository (force=True removes images first)."""
    if dry_run:
        logger.info("[DRY-RUN] Would delete repository: %s", name)
        return None
    try:
        response = client.delete_repository(repositoryName=name, force=force)
        logger.info("Deleted ECR repository: %s", name)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to delete repository %s: %s", name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Delete an ECR repository")
    parser.add_argument("--name", required=True, help="Repository name")
    args = parser.parse_args()
    client = get_client("ecr", args.profile, args.region)
    delete_repository(client, args.name, dry_run=args.dry_run)
