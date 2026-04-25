"""Delete an Auto Scaling group."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_asg(client, name, force=False, dry_run=False):
    """Delete an Auto Scaling group."""
    if dry_run:
        logger.info("[DRY-RUN] Would delete ASG: %s", name)
        return None
    try:
        response = client.delete_auto_scaling_group(
            AutoScalingGroupName=name, ForceDelete=force
        )
        logger.info("Deleted Auto Scaling group: %s", name)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to delete ASG %s: %s", name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Delete an Auto Scaling group")
    parser.add_argument("--name", required=True, help="ASG name")
    parser.add_argument("--force", action="store_true", help="Force delete (terminate instances)")
    args = parser.parse_args()
    client = get_client("autoscaling", args.profile, args.region)
    delete_asg(client, args.name, args.force, args.dry_run)
