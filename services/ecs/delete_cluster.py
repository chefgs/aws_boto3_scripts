"""Delete an ECS cluster."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_cluster(client, cluster_name, dry_run=False):
    """Delete the specified ECS cluster."""
    if dry_run:
        logger.info("[DRY-RUN] Would delete cluster: %s", cluster_name)
        return None
    try:
        response = client.delete_cluster(cluster=cluster_name)
        logger.info("Deleted cluster: %s", cluster_name)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to delete cluster %s: %s", cluster_name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Delete an ECS cluster")
    parser.add_argument("--name", required=True, help="Cluster name or ARN")
    args = parser.parse_args()
    client = get_client("ecs", args.profile, args.region)
    delete_cluster(client, args.name, args.dry_run)
