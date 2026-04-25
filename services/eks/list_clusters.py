"""List EKS cluster names."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_clusters(client):
    """Return a list of EKS cluster names.

    Parameters
    ----------
    client : boto3 EKS client

    Returns
    -------
    list of str  — cluster names
    """
    try:
        paginator = client.get_paginator("list_clusters")
        names = []
        for page in paginator.paginate():
            names.extend(page.get("clusters", []))
        for name in names:
            logger.info("EKS cluster: %s", name)
        return names
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list EKS clusters: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List EKS clusters")
    args = parser.parse_args()
    client = get_client("eks", args.profile, args.region)
    list_clusters(client)
