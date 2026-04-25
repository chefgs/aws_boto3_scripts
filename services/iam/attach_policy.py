"""Attach a managed policy to an IAM user or role."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def attach_policy(client, target_type, target_name, policy_arn):
    """Attach a managed policy to a user or role.

    Args:
        client: IAM boto3 client.
        target_type: 'user' or 'role'.
        target_name: User or role name.
        policy_arn: ARN of the managed policy.
    """
    try:
        if target_type == "user":
            client.attach_user_policy(UserName=target_name, PolicyArn=policy_arn)
        elif target_type == "role":
            client.attach_role_policy(RoleName=target_name, PolicyArn=policy_arn)
        else:
            raise ValueError(f"Unknown target_type: {target_type}")
        logger.info("Attached policy %s to %s %s", policy_arn, target_type, target_name)
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to attach policy: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Attach a managed policy to a user or role")
    parser.add_argument(
        "--target-type", required=True, choices=["user", "role"], help="user or role"
    )
    parser.add_argument("--target-name", required=True, help="User or role name")
    parser.add_argument("--policy-arn", required=True, help="Managed policy ARN")
    args = parser.parse_args()
    client = get_client("iam", args.profile, args.region)
    attach_policy(client, args.target_type, args.target_name, args.policy_arn)
