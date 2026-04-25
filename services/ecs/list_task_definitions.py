"""List ECS task definition ARNs."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_task_definitions(client, family_prefix=None, status="ACTIVE"):
    """Return a list of ECS task definition ARNs.

    Parameters
    ----------
    client        : boto3 ECS client
    family_prefix : optional family name prefix to filter results
    status        : 'ACTIVE' or 'INACTIVE' (default: 'ACTIVE')

    Returns
    -------
    list of str  — task definition ARNs
    """
    try:
        kwargs = {"status": status}
        if family_prefix:
            kwargs["familyPrefix"] = family_prefix
        paginator = client.get_paginator("list_task_definitions")
        arns = []
        for page in paginator.paginate(**kwargs):
            arns.extend(page.get("taskDefinitionArns", []))
        for arn in arns:
            logger.info("Task definition: %s", arn)
        return arns
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list task definitions: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List ECS task definitions")
    parser.add_argument("--family-prefix", default=None, help="Filter by family prefix")
    parser.add_argument(
        "--status", default="ACTIVE", choices=["ACTIVE", "INACTIVE"], help="Filter by status"
    )
    args = parser.parse_args()
    client = get_client("ecs", args.profile, args.region)
    list_task_definitions(client, family_prefix=args.family_prefix, status=args.status)
