"""Get an item from a DynamoDB table."""
import json
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def get_item(client, table_name, key):
    """Get an item by key from the specified DynamoDB table."""
    try:
        response = client.get_item(TableName=table_name, Key=key)
        item = response.get("Item")
        if item:
            logger.info("Got item from %s: %s", table_name, item)
        else:
            logger.info("Item not found in table: %s", table_name)
        return item
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to get item from %s: %s", table_name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Get an item from a DynamoDB table")
    parser.add_argument("--table-name", required=True, help="Table name")
    parser.add_argument(
        "--key", required=True,
        help='Key as JSON string with DynamoDB type annotations, e.g. \'{"id": {"S": "1"}}\'',
    )
    args = parser.parse_args()
    client = get_client("dynamodb", args.profile, args.region)
    get_item(client, args.table_name, json.loads(args.key))
