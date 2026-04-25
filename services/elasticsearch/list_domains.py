"""List Elasticsearch domains."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_domains(client):
    """Return a list of Elasticsearch domain names."""
    try:
        response = client.list_domain_names()
        domains = [d["DomainName"] for d in response.get("DomainNames", [])]
        for name in domains:
            logger.info("ES Domain: %s", name)
        return domains
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list ES domains: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List Elasticsearch domains")
    args = parser.parse_args()
    client = get_client("es", args.profile, args.region)
    list_domains(client)
