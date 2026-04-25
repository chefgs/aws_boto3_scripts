"""Delete an EKS cluster."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_cluster(client, name, dry_run=False):
    """Delete an EKS cluster by name.

    Parameters
    ----------
    client  : boto3 EKS client
    name    : cluster name
    dry_run : if True, log the action without making changes

    Returns
    -------
    dict  — the cluster object from the DeleteCluster response, or None on dry_run
    """
    if dry_run:
        logger.info("[DRY-RUN] Would delete EKS cluster: %s", name)
        return None
    try:
        response = client.delete_cluster(name=name)
        cluster = response["cluster"]
        logger.info(
            "Deleted EKS cluster: %s (status: %s)", name, cluster.get("status")
        )
        return cluster
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to delete EKS cluster %s: %s", name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Delete an EKS cluster")
    parser.add_argument("--name", required=True, help="Cluster name")
    args = parser.parse_args()
    client = get_client("eks", args.profile, args.region)
    delete_cluster(client, args.name, dry_run=args.dry_run)
