"""List VPCs."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_vpcs(client):
    """Return a list of VPC dicts."""
    try:
        response = client.describe_vpcs()
        vpcs = response.get("Vpcs", [])
        for vpc in vpcs:
            logger.info("VPC %s | CIDR=%s | default=%s", vpc["VpcId"], vpc["CidrBlock"], vpc.get("IsDefault", False))
        return vpcs
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list VPCs: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List VPCs")
    args = parser.parse_args()
    client = get_client("ec2", args.profile, args.region)
    list_vpcs(client)
