"""List SSM Parameter Store parameters."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_parameters(client, path=None):
    """Return a list of SSM parameter metadata dicts."""
    try:
        params = []
        if path:
            paginator = client.get_paginator("get_parameters_by_path")
            for page in paginator.paginate(Path=path, Recursive=True):
                params.extend(page.get("Parameters", []))
        else:
            paginator = client.get_paginator("describe_parameters")
            for page in paginator.paginate():
                params.extend(page.get("Parameters", []))
        for p in params:
            logger.info("Parameter: %s | type=%s", p["Name"], p.get("Type"))
        return params
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list parameters: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List SSM Parameter Store parameters")
    parser.add_argument("--path", default=None, help="Parameter path prefix (e.g. /myapp)")
    args = parser.parse_args()
    client = get_client("ssm", args.profile, args.region)
    list_parameters(client, args.path)
