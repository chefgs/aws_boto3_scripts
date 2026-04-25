"""Delete a CloudFormation stack."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_stack(client, stack_name, dry_run=False):
    """Delete the specified CloudFormation stack."""
    if dry_run:
        logger.info("[DRY-RUN] Would delete stack: %s", stack_name)
        return None
    try:
        response = client.delete_stack(StackName=stack_name)
        logger.info("Deletion initiated for stack: %s", stack_name)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to delete stack %s: %s", stack_name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Delete a CloudFormation stack")
    parser.add_argument("--stack-name", required=True, help="Stack name")
    args = parser.parse_args()
    client = get_client("cloudformation", args.profile, args.region)
    delete_stack(client, args.stack_name, args.dry_run)
