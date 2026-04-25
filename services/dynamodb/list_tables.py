"""List DynamoDB tables."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_tables(client):
    """Return a list of DynamoDB table names."""
    try:
        paginator = client.get_paginator("list_tables")
        tables = []
        for page in paginator.paginate():
            tables.extend(page.get("TableNames", []))
        for name in tables:
            logger.info("Table: %s", name)
        return tables
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list tables: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List DynamoDB tables")
    args = parser.parse_args()
    client = get_client("dynamodb", args.profile, args.region)
    list_tables(client)
