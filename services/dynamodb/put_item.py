"""Put an item into a DynamoDB table."""
import json
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def put_item(client, table_name, item):
    """Put an item (dict) into the specified DynamoDB table."""
    try:
        response = client.put_item(TableName=table_name, Item=item)
        logger.info("Put item into table: %s", table_name)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to put item in %s: %s", table_name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Put an item into a DynamoDB table")
    parser.add_argument("--table-name", required=True, help="Table name")
    parser.add_argument(
        "--item", required=True,
        help='Item as JSON string with DynamoDB type annotations, e.g. \'{"id": {"S": "1"}}\'',
    )
    args = parser.parse_args()
    client = get_client("dynamodb", args.profile, args.region)
    put_item(client, args.table_name, json.loads(args.item))
