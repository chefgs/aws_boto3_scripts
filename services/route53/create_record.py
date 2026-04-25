"""Create a DNS record in a Route 53 hosted zone."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_record(client, zone_id, name, record_type, value, ttl=300):
    """Create or update a DNS record in the given hosted zone."""
    try:
        response = client.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "UPSERT",
                        "ResourceRecordSet": {
                            "Name": name,
                            "Type": record_type,
                            "TTL": ttl,
                            "ResourceRecords": [{"Value": value}],
                        },
                    }
                ]
            },
        )
        status = response["ChangeInfo"]["Status"]
        logger.info("Created record %s %s -> %s | status=%s", record_type, name, value, status)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create record %s: %s", name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create a Route 53 DNS record")
    parser.add_argument("--zone-id", required=True, help="Hosted zone ID")
    parser.add_argument("--name", required=True, help="Record name (e.g. www.example.com)")
    parser.add_argument("--type", required=True, dest="record_type", help="Record type (A, CNAME, …)")
    parser.add_argument("--value", required=True, help="Record value (IP or domain)")
    parser.add_argument("--ttl", type=int, default=300, help="TTL in seconds")
    args = parser.parse_args()
    client = get_client("route53", args.profile, args.region)
    create_record(client, args.zone_id, args.name, args.record_type, args.value, args.ttl)
