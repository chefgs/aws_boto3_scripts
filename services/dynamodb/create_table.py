"""Create a DynamoDB table."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_table(client, table_name, partition_key, sort_key=None):
    """Create a DynamoDB table and return the table description.

    Args:
        client: DynamoDB boto3 client.
        table_name: Name of the table.
        partition_key: Name of the partition key (String type).
        sort_key: Optional sort key name (String type).
    """
    key_schema = [{"AttributeName": partition_key, "KeyType": "HASH"}]
    attr_defs = [{"AttributeName": partition_key, "AttributeType": "S"}]
    if sort_key:
        key_schema.append({"AttributeName": sort_key, "KeyType": "RANGE"})
        attr_defs.append({"AttributeName": sort_key, "AttributeType": "S"})
    try:
        response = client.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attr_defs,
            BillingMode="PAY_PER_REQUEST",
        )
        status = response["TableDescription"]["TableStatus"]
        logger.info("Created DynamoDB table: %s | status=%s", table_name, status)
        return response["TableDescription"]
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create table %s: %s", table_name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create a DynamoDB table")
    parser.add_argument("--table-name", required=True, help="Table name")
    parser.add_argument("--partition-key", required=True, help="Partition key attribute name")
    parser.add_argument("--sort-key", default=None, help="Sort key attribute name (optional)")
    args = parser.parse_args()
    client = get_client("dynamodb", args.profile, args.region)
    create_table(client, args.table_name, args.partition_key, args.sort_key)
