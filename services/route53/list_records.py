"""List DNS records in a Route 53 hosted zone."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_records(client, zone_id):
    """Return a list of resource record sets for the given hosted zone."""
    try:
        paginator = client.get_paginator("list_resource_record_sets")
        records = []
        for page in paginator.paginate(HostedZoneId=zone_id):
            records.extend(page.get("ResourceRecordSets", []))
        for r in records:
            logger.info("Record: %s %s", r["Type"], r["Name"])
        return records
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list records in zone %s: %s", zone_id, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List Route 53 DNS records")
    parser.add_argument("--zone-id", required=True, help="Hosted zone ID")
    args = parser.parse_args()
    client = get_client("route53", args.profile, args.region)
    list_records(client, args.zone_id)
