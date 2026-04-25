"""Create one or more EC2 instances."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_instance(client, ami, instance_type, key_name, count=1):
    """Launch EC2 instances and return the list of instance IDs."""
    try:
        response = client.run_instances(
            ImageId=ami,
            InstanceType=instance_type,
            KeyName=key_name,
            MinCount=count,
            MaxCount=count,
        )
        ids = [i["InstanceId"] for i in response["Instances"]]
        for iid in ids:
            logger.info("Launched instance: %s", iid)
        return ids
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create instance: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create EC2 instance(s)")
    parser.add_argument("--ami", required=True, help="AMI ID")
    parser.add_argument("--instance-type", default="t2.micro", help="Instance type")
    parser.add_argument("--key-name", required=True, help="Key pair name")
    parser.add_argument("--count", type=int, default=1, help="Number of instances")
    args = parser.parse_args()
    client = get_client("ec2", args.profile, args.region)
    create_instance(client, args.ami, args.instance_type, args.key_name, args.count)
