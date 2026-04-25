"""Create an IAM role with a basic trust policy."""
import json
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_role(client, role_name, service_principal="ec2.amazonaws.com"):
    """Create an IAM role with a trust policy for the given service principal."""
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": service_principal},
                "Action": "sts:AssumeRole",
            }
        ],
    }
    try:
        response = client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=f"Role for {service_principal}",
        )
        arn = response["Role"]["Arn"]
        logger.info("Created IAM role: %s (%s)", role_name, arn)
        return response["Role"]
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create role %s: %s", role_name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create an IAM role")
    parser.add_argument("--role-name", required=True, help="IAM role name")
    parser.add_argument(
        "--service",
        default="ec2.amazonaws.com",
        help="Service principal (e.g. ec2.amazonaws.com)",
    )
    args = parser.parse_args()
    client = get_client("iam", args.profile, args.region)
    create_role(client, args.role_name, args.service)
