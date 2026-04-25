"""Delete a Route 53 hosted zone."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_hosted_zone(client, zone_id, dry_run=False):
    """Delete the specified hosted zone."""
    if dry_run:
        logger.info("[DRY-RUN] Would delete hosted zone: %s", zone_id)
        return None
    try:
        response = client.delete_hosted_zone(Id=zone_id)
        logger.info("Deleted hosted zone: %s", zone_id)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to delete hosted zone %s: %s", zone_id, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Delete a Route 53 hosted zone")
    parser.add_argument("--zone-id", required=True, help="Hosted zone ID")
    args = parser.parse_args()
    client = get_client("route53", args.profile, args.region)
    delete_hosted_zone(client, args.zone_id, args.dry_run)
