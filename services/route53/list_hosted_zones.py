"""List Route 53 hosted zones."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_hosted_zones(client):
    """Return a list of hosted zone dicts."""
    try:
        paginator = client.get_paginator("list_hosted_zones")
        zones = []
        for page in paginator.paginate():
            zones.extend(page.get("HostedZones", []))
        for zone in zones:
            logger.info("Zone: %s (%s)", zone["Name"], zone["Id"])
        return zones
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list hosted zones: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List Route 53 hosted zones")
    args = parser.parse_args()
    client = get_client("route53", args.profile, args.region)
    list_hosted_zones(client)
