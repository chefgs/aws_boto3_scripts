"""Schedule deletion of a KMS key."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_key(client, key_id, pending_days=30, dry_run=False):
    """Schedule a KMS key for deletion."""
    if dry_run:
        logger.info("[DRY-RUN] Would schedule deletion of key: %s", key_id)
        return None
    try:
        response = client.schedule_key_deletion(
            KeyId=key_id, PendingWindowInDays=pending_days
        )
        deletion_date = response.get("DeletionDate")
        logger.info("Key %s scheduled for deletion on: %s", key_id, deletion_date)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to schedule key deletion %s: %s", key_id, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Schedule KMS key deletion")
    parser.add_argument("--key-id", required=True, help="KMS key ID or ARN")
    parser.add_argument(
        "--pending-days", type=int, default=30, help="Days before deletion (7-30)"
    )
    args = parser.parse_args()
    client = get_client("kms", args.profile, args.region)
    delete_key(client, args.key_id, args.pending_days, args.dry_run)
