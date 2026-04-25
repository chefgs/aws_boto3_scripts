"""Delete an SSM Parameter Store parameter."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_parameter(client, name, dry_run=False):
    """Delete the specified SSM parameter."""
    if dry_run:
        logger.info("[DRY-RUN] Would delete parameter: %s", name)
        return None
    try:
        response = client.delete_parameter(Name=name)
        logger.info("Deleted SSM parameter: %s", name)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to delete parameter %s: %s", name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Delete an SSM Parameter Store parameter")
    parser.add_argument("--name", required=True, help="Parameter name")
    args = parser.parse_args()
    client = get_client("ssm", args.profile, args.region)
    delete_parameter(client, args.name, args.dry_run)
