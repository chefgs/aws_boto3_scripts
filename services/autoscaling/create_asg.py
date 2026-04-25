"""Create an Auto Scaling group."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_asg(client, name, launch_template_id, min_size, max_size, desired, subnets):
    """Create an Auto Scaling group and return the response."""
    try:
        response = client.create_auto_scaling_group(
            AutoScalingGroupName=name,
            LaunchTemplate={"LaunchTemplateId": launch_template_id},
            MinSize=min_size,
            MaxSize=max_size,
            DesiredCapacity=desired,
            VPCZoneIdentifier=subnets,
        )
        logger.info("Created Auto Scaling group: %s", name)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create ASG %s: %s", name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create an Auto Scaling group")
    parser.add_argument("--name", required=True, help="ASG name")
    parser.add_argument("--launch-template-id", required=True, help="Launch template ID")
    parser.add_argument("--min", type=int, default=1, dest="min_size", help="Min instances")
    parser.add_argument("--max", type=int, default=3, dest="max_size", help="Max instances")
    parser.add_argument("--desired", type=int, default=1, help="Desired capacity")
    parser.add_argument("--subnets", required=True, help="Comma-separated subnet IDs")
    args = parser.parse_args()
    client = get_client("autoscaling", args.profile, args.region)
    create_asg(
        client, args.name, args.launch_template_id,
        args.min_size, args.max_size, args.desired, args.subnets
    )
