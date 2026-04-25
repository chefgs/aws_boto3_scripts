"""Delete a DynamoDB table."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_table(client, table_name, dry_run=False):
    """Delete the specified DynamoDB table."""
    if dry_run:
        logger.info("[DRY-RUN] Would delete table: %s", table_name)
        return None
    try:
        response = client.delete_table(TableName=table_name)
        logger.info("Deleted table: %s", table_name)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to delete table %s: %s", table_name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Delete a DynamoDB table")
    parser.add_argument("--table-name", required=True, help="Table name")
    args = parser.parse_args()
    client = get_client("dynamodb", args.profile, args.region)
    delete_table(client, args.table_name, args.dry_run)
