"""Delete an Elasticsearch domain."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_domain(client, domain_name, dry_run=False):
    """Delete the specified Elasticsearch domain."""
    if dry_run:
        logger.info("[DRY-RUN] Would delete ES domain: %s", domain_name)
        return None
    try:
        response = client.delete_elasticsearch_domain(DomainName=domain_name)
        logger.info("Deleted ES domain: %s", domain_name)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to delete ES domain %s: %s", domain_name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Delete an Elasticsearch domain")
    parser.add_argument("--name", required=True, help="Domain name")
    args = parser.parse_args()
    client = get_client("es", args.profile, args.region)
    delete_domain(client, args.name, args.dry_run)
