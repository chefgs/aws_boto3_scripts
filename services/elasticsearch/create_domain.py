"""Create an Elasticsearch domain."""
import json
import logging
import random

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_account_id, get_client

logger = logging.getLogger(__name__)


def create_domain(client, domain_name, version="7.10", instance_type="t3.small.elasticsearch", region="us-east-1", account_id=None):
    """Create an Elasticsearch domain and return the response."""
    if account_id is None:
        account_id = "000000000000"
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["es:*"],
                "Resource": f"arn:aws:es:{region}:{account_id}:domain/{domain_name}/*",
            }
        ],
    }
    try:
        response = client.create_elasticsearch_domain(
            DomainName=domain_name,
            ElasticsearchVersion=version,
            ElasticsearchClusterConfig={
                "InstanceType": instance_type,
                "InstanceCount": 1,
                "DedicatedMasterEnabled": False,
                "ZoneAwarenessEnabled": False,
            },
            EBSOptions={"EBSEnabled": True, "VolumeType": "gp2", "VolumeSize": 10},
            AccessPolicies=json.dumps(policy),
        )
        logger.info("Created Elasticsearch domain: %s", domain_name)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create ES domain %s: %s", domain_name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create an Elasticsearch domain")
    parser.add_argument("--name", default=None, help="Domain name")
    parser.add_argument("--version", default="7.10", help="Elasticsearch version")
    parser.add_argument(
        "--instance-type", default="t3.small.elasticsearch", help="Instance type"
    )
    args = parser.parse_args()
    client = get_client("es", args.profile, args.region)
    acct = get_account_id(args.profile, args.region)
    name = args.name or "boto3es" + str(random.randint(0, 99999))
    create_domain(client, name, args.version, args.instance_type, args.region, acct)
