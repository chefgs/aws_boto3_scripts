"""Get a parameter from SSM Parameter Store."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def get_parameter(client, name, with_decryption=True):
    """Retrieve an SSM parameter value."""
    try:
        response = client.get_parameter(Name=name, WithDecryption=with_decryption)
        value = response["Parameter"]["Value"]
        logger.info("Got SSM parameter: %s", name)
        return value
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to get parameter %s: %s", name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Get an SSM Parameter Store parameter")
    parser.add_argument("--name", required=True, help="Parameter name (path)")
    parser.add_argument(
        "--with-decryption",
        action="store_true",
        default=True,
        help="Decrypt SecureString values",
    )
    args = parser.parse_args()
    client = get_client("ssm", args.profile, args.region)
    get_parameter(client, args.name, args.with_decryption)
