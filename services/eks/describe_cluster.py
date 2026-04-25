"""Describe an EKS cluster."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def describe_cluster(client, name):
    """Return the description dict for an EKS cluster.

    Parameters
    ----------
    client : boto3 EKS client
    name   : cluster name

    Returns
    -------
    dict  — the cluster object, or None if not found
    """
    try:
        response = client.describe_cluster(name=name)
        cluster = response.get("cluster")
        if not cluster:
            logger.warning("EKS cluster not found: %s", name)
            return None
        logger.info(
            "EKS cluster %s: status=%s, version=%s",
            name,
            cluster.get("status"),
            cluster.get("version"),
        )
        return cluster
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to describe EKS cluster %s: %s", name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Describe an EKS cluster")
    parser.add_argument("--name", required=True, help="Cluster name")
    args = parser.parse_args()
    client = get_client("eks", args.profile, args.region)
    describe_cluster(client, args.name)
