"""Delete a Lambda function."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_function(client, function_name, dry_run=False):
    """Delete the specified Lambda function."""
    if dry_run:
        logger.info("[DRY-RUN] Would delete function: %s", function_name)
        return None
    try:
        response = client.delete_function(FunctionName=function_name)
        logger.info("Deleted Lambda function: %s", function_name)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to delete function %s: %s", function_name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Delete a Lambda function")
    parser.add_argument("--function-name", required=True, help="Function name")
    args = parser.parse_args()
    client = get_client("lambda", args.profile, args.region)
    delete_function(client, args.function_name, args.dry_run)
