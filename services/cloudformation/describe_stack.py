"""Describe a CloudFormation stack."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def describe_stack(client, stack_name):
    """Return the stack description dict."""
    try:
        response = client.describe_stacks(StackName=stack_name)
        stacks = response.get("Stacks", [])
        if not stacks:
            logger.warning("Stack not found: %s", stack_name)
            return None
        stack = stacks[0]
        logger.info("Stack %s | status=%s", stack_name, stack["StackStatus"])
        return stack
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to describe stack %s: %s", stack_name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Describe a CloudFormation stack")
    parser.add_argument("--stack-name", required=True, help="Stack name")
    args = parser.parse_args()
    client = get_client("cloudformation", args.profile, args.region)
    describe_stack(client, args.stack_name)
