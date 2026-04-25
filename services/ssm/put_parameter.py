"""Put a parameter in SSM Parameter Store."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def put_parameter(client, name, value, param_type="String", overwrite=True):
    """Create or update an SSM parameter."""
    try:
        response = client.put_parameter(
            Name=name,
            Value=value,
            Type=param_type,
            Overwrite=overwrite,
        )
        logger.info("Put SSM parameter: %s (version %s)", name, response.get("Version"))
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to put parameter %s: %s", name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Put an SSM Parameter Store parameter")
    parser.add_argument("--name", required=True, help="Parameter name (path)")
    parser.add_argument("--value", required=True, help="Parameter value")
    parser.add_argument(
        "--type",
        default="String",
        choices=["String", "StringList", "SecureString"],
        dest="param_type",
        help="Parameter type",
    )
    args = parser.parse_args()
    client = get_client("ssm", args.profile, args.region)
    put_parameter(client, args.name, args.value, args.param_type)
