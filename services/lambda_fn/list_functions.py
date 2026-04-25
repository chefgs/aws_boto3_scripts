"""List Lambda functions."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_functions(client):
    """Return a list of Lambda function configurations."""
    try:
        paginator = client.get_paginator("list_functions")
        functions = []
        for page in paginator.paginate():
            functions.extend(page.get("Functions", []))
        for fn in functions:
            logger.info("Function: %s | runtime=%s", fn["FunctionName"], fn.get("Runtime"))
        return functions
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list Lambda functions: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List Lambda functions")
    args = parser.parse_args()
    client = get_client("lambda", args.profile, args.region)
    list_functions(client)
