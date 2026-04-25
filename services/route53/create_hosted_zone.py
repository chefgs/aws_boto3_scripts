"""Create a Route 53 hosted zone."""
import logging
import uuid

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_hosted_zone(client, name, private=False):
    """Create a Route 53 hosted zone and return the zone ID."""
    try:
        kwargs = {
            "Name": name,
            "CallerReference": str(uuid.uuid4()),
        }
        if private:
            kwargs["HostedZoneConfig"] = {"PrivateZone": True}
        response = client.create_hosted_zone(**kwargs)
        zone_id = response["HostedZone"]["Id"]
        logger.info("Created hosted zone: %s (%s)", name, zone_id)
        return zone_id
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create hosted zone %s: %s", name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create a Route 53 hosted zone")
    parser.add_argument("--name", required=True, help="Domain name (e.g. example.com)")
    parser.add_argument("--private", action="store_true", help="Create a private zone")
    args = parser.parse_args()
    client = get_client("route53", args.profile, args.region)
    create_hosted_zone(client, args.name, args.private)
