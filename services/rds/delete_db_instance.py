"""Delete an RDS DB instance."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_db_instance(client, db_id, skip_final_snapshot=True, dry_run=False):
    """Delete an RDS DB instance."""
    if dry_run:
        logger.info("[DRY-RUN] Would delete DB instance: %s", db_id)
        return None
    try:
        kwargs = {
            "DBInstanceIdentifier": db_id,
            "SkipFinalSnapshot": skip_final_snapshot,
        }
        if not skip_final_snapshot:
            kwargs["FinalDBSnapshotIdentifier"] = f"{db_id}-final-snapshot"
        response = client.delete_db_instance(**kwargs)
        status = response["DBInstance"]["DBInstanceStatus"]
        logger.info("DB instance %s is now: %s", db_id, status)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to delete DB instance %s: %s", db_id, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Delete an RDS DB instance")
    parser.add_argument("--db-id", required=True, help="DB instance identifier")
    parser.add_argument(
        "--skip-final-snapshot",
        action="store_true",
        default=True,
        help="Skip final snapshot",
    )
    args = parser.parse_args()
    client = get_client("rds", args.profile, args.region)
    delete_db_instance(client, args.db_id, args.skip_final_snapshot, args.dry_run)
