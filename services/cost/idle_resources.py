"""Detect idle / underutilised AWS resources to identify cost-saving opportunities."""
import logging
from datetime import datetime, timedelta, timezone

import botocore.exceptions

from services.cost.pricing_estimator import (
    estimate_ebs_monthly,
    estimate_ec2_monthly,
    estimate_nat_gateway_monthly,
    load_static_prices,
)

logger = logging.getLogger(__name__)

_DEFAULT_CPU_THRESHOLD = 5.0   # percent
_DEFAULT_IDLE_DAYS = 14        # CloudWatch lookback window
_DEFAULT_SNAPSHOT_AGE_DAYS = 90


# ---------------------------------------------------------------------------
# CloudWatch helpers
# ---------------------------------------------------------------------------

def _get_average_metric(cw_client, namespace, metric_name, dimensions, days):
    """Return the average of a CloudWatch metric over the last *days* days.

    Returns None when no datapoints are available.
    """
    end = datetime.now(tz=timezone.utc)
    start = end - timedelta(days=days)
    try:
        resp = cw_client.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric_name,
            Dimensions=dimensions,
            StartTime=start,
            EndTime=end,
            Period=int(days * 86400),
            Statistics=["Average"],
        )
        datapoints = resp.get("Datapoints", [])
        if not datapoints:
            return None
        return datapoints[0]["Average"]
    except botocore.exceptions.ClientError as exc:
        logger.warning("CloudWatch metric error (%s/%s): %s", namespace, metric_name, exc)
        return None


# ---------------------------------------------------------------------------
# EC2
# ---------------------------------------------------------------------------

def find_idle_ec2_instances(ec2_client, cw_client,
                             cpu_threshold=_DEFAULT_CPU_THRESHOLD,
                             days=_DEFAULT_IDLE_DAYS,
                             dry_run=False):
    """Return EC2 instances that are stopped or have very low average CPU.

    Returns
    -------
    list of dicts with keys:
        instance_id, instance_type, state, avg_cpu_pct,
        reason, estimated_monthly_waste_usd, recommendation
    """
    if dry_run:
        logger.info(
            "[DRY-RUN] Would call ec2.describe_instances + cloudwatch.get_metric_statistics "
            "(CPU threshold=%.1f%%, lookback=%d days)", cpu_threshold, days,
        )
        return []

    findings = []
    prices = load_static_prices()

    try:
        paginator = ec2_client.get_paginator("describe_instances")
        for page in paginator.paginate():
            for reservation in page["Reservations"]:
                for inst in reservation["Instances"]:
                    instance_id = inst["InstanceId"]
                    instance_type = inst.get("InstanceType", "unknown")
                    state = inst["State"]["Name"]
                    hourly = prices.get("ec2", {}).get(instance_type, {}).get("linux", 0.0)
                    monthly = hourly * 730

                    if state == "stopped":
                        findings.append({
                            "instance_id": instance_id,
                            "instance_type": instance_type,
                            "state": state,
                            "avg_cpu_pct": None,
                            "reason": "Instance is stopped",
                            "estimated_monthly_waste_usd": monthly,
                            "recommendation": "Terminate if not needed or schedule auto-stop",
                        })
                        continue

                    if state != "running":
                        continue

                    avg_cpu = _get_average_metric(
                        cw_client,
                        "AWS/EC2",
                        "CPUUtilization",
                        [{"Name": "InstanceId", "Value": instance_id}],
                        days,
                    )

                    if avg_cpu is not None and avg_cpu < cpu_threshold:
                        findings.append({
                            "instance_id": instance_id,
                            "instance_type": instance_type,
                            "state": state,
                            "avg_cpu_pct": round(avg_cpu, 2),
                            "reason": f"Average CPU {avg_cpu:.1f}% < {cpu_threshold}% over {days} days",
                            "estimated_monthly_waste_usd": monthly,
                            "recommendation": "Right-size to a smaller instance type or terminate",
                        })

    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to scan EC2 instances: %s", exc)
        raise

    logger.info("Found %d idle/underutilised EC2 instance(s)", len(findings))
    return findings


def find_unattached_ebs_volumes(ec2_client, dry_run=False):
    """Return EBS volumes in 'available' (unattached) state.

    Returns
    -------
    list of dicts with keys:
        volume_id, volume_type, size_gb, state,
        estimated_monthly_waste_usd, recommendation
    """
    if dry_run:
        logger.info("[DRY-RUN] Would call ec2.describe_volumes(Filters=[state=available])")
        return []

    findings = []
    try:
        paginator = ec2_client.get_paginator("describe_volumes")
        for page in paginator.paginate(Filters=[{"Name": "status", "Values": ["available"]}]):
            for vol in page.get("Volumes", []):
                est = estimate_ebs_monthly(vol.get("VolumeType", "gp2"), vol["Size"])
                monthly = est["monthly_cost_usd"] if est else 0.0
                findings.append({
                    "volume_id": vol["VolumeId"],
                    "volume_type": vol.get("VolumeType", "unknown"),
                    "size_gb": vol["Size"],
                    "state": vol["State"],
                    "estimated_monthly_waste_usd": monthly,
                    "recommendation": "Delete unattached volume or create a snapshot and delete",
                })
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to scan EBS volumes: %s", exc)
        raise

    logger.info("Found %d unattached EBS volume(s)", len(findings))
    return findings


def find_unused_elastic_ips(ec2_client, dry_run=False):
    """Return Elastic IP addresses not associated with any instance or network interface.

    Returns
    -------
    list of dicts with keys:
        allocation_id, public_ip, estimated_monthly_waste_usd, recommendation
    """
    if dry_run:
        logger.info("[DRY-RUN] Would call ec2.describe_addresses()")
        return []

    findings = []
    prices = load_static_prices()
    hourly_rate = prices.get("eip", {}).get("idle_per_hour", 0.005)

    try:
        resp = ec2_client.describe_addresses()
        for addr in resp.get("Addresses", []):
            if not addr.get("AssociationId"):
                monthly = hourly_rate * 730
                findings.append({
                    "allocation_id": addr.get("AllocationId", ""),
                    "public_ip": addr.get("PublicIp", ""),
                    "estimated_monthly_waste_usd": monthly,
                    "recommendation": "Release the unused Elastic IP address",
                })
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to scan Elastic IPs: %s", exc)
        raise

    logger.info("Found %d unused Elastic IP(s)", len(findings))
    return findings


def find_old_snapshots(ec2_client, age_days=_DEFAULT_SNAPSHOT_AGE_DAYS, dry_run=False):
    """Return EBS snapshots older than *age_days* days that are not in use by an AMI.

    Returns
    -------
    list of dicts with keys:
        snapshot_id, volume_size_gb, start_time, age_days, recommendation
    """
    if dry_run:
        logger.info(
            "[DRY-RUN] Would call ec2.describe_snapshots(OwnerIds=['self']) "
            "and filter by age > %d days", age_days,
        )
        return []

    # Collect AMI snapshot IDs so we can exclude them
    ami_snapshot_ids = set()
    try:
        img_paginator = ec2_client.get_paginator("describe_images")
        for page in img_paginator.paginate(Owners=["self"]):
            for image in page.get("Images", []):
                for bdm in image.get("BlockDeviceMappings", []):
                    snap_id = bdm.get("Ebs", {}).get("SnapshotId")
                    if snap_id:
                        ami_snapshot_ids.add(snap_id)
    except botocore.exceptions.ClientError as exc:
        logger.warning("Could not list owned AMIs: %s", exc)

    findings = []
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=age_days)
    try:
        paginator = ec2_client.get_paginator("describe_snapshots")
        for page in paginator.paginate(OwnerIds=["self"]):
            for snap in page.get("Snapshots", []):
                start = snap["StartTime"]
                if start.tzinfo is None:
                    start = start.replace(tzinfo=timezone.utc)
                if start < cutoff and snap["SnapshotId"] not in ami_snapshot_ids:
                    delta_days = (datetime.now(tz=timezone.utc) - start).days
                    findings.append({
                        "snapshot_id": snap["SnapshotId"],
                        "volume_size_gb": snap.get("VolumeSize", 0),
                        "start_time": start.isoformat(),
                        "age_days": delta_days,
                        "recommendation": f"Delete snapshot older than {age_days} days",
                    })
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to scan snapshots: %s", exc)
        raise

    logger.info("Found %d old snapshot(s) (>%d days)", len(findings), age_days)
    return findings


# ---------------------------------------------------------------------------
# RDS
# ---------------------------------------------------------------------------

def find_idle_rds_instances(rds_client, cw_client,
                             cpu_threshold=_DEFAULT_CPU_THRESHOLD,
                             days=_DEFAULT_IDLE_DAYS,
                             dry_run=False):
    """Return RDS instances that are stopped or have very low average CPU.

    Returns
    -------
    list of dicts with keys:
        db_instance_id, db_instance_class, engine, state, multi_az,
        avg_cpu_pct, reason, estimated_monthly_waste_usd, recommendation
    """
    if dry_run:
        logger.info(
            "[DRY-RUN] Would call rds.describe_db_instances + cloudwatch.get_metric_statistics"
        )
        return []

    findings = []
    prices = load_static_prices()

    try:
        paginator = rds_client.get_paginator("describe_db_instances")
        for page in paginator.paginate():
            for db in page.get("DBInstances", []):
                db_id = db["DBInstanceIdentifier"]
                cls = db["DBInstanceClass"]
                engine = db.get("Engine", "")
                status = db.get("DBInstanceStatus", "")
                multi_az = db.get("MultiAZ", False)
                az_key = "multi_az" if multi_az else "single"
                hourly = prices.get("rds", {}).get(cls, {}).get(az_key, 0.0)
                monthly = hourly * 730

                if status == "stopped":
                    findings.append({
                        "db_instance_id": db_id,
                        "db_instance_class": cls,
                        "engine": engine,
                        "state": status,
                        "multi_az": multi_az,
                        "avg_cpu_pct": None,
                        "reason": "DB instance is stopped",
                        "estimated_monthly_waste_usd": monthly,
                        "recommendation": "Delete or snapshot-and-delete if not needed",
                    })
                    continue

                if status != "available":
                    continue

                avg_cpu = _get_average_metric(
                    cw_client,
                    "AWS/RDS",
                    "CPUUtilization",
                    [{"Name": "DBInstanceIdentifier", "Value": db_id}],
                    days,
                )

                if avg_cpu is not None and avg_cpu < cpu_threshold:
                    findings.append({
                        "db_instance_id": db_id,
                        "db_instance_class": cls,
                        "engine": engine,
                        "state": status,
                        "multi_az": multi_az,
                        "avg_cpu_pct": round(avg_cpu, 2),
                        "reason": f"Average CPU {avg_cpu:.1f}% < {cpu_threshold}% over {days} days",
                        "estimated_monthly_waste_usd": monthly,
                        "recommendation": "Right-size or consider Aurora Serverless",
                    })

    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to scan RDS instances: %s", exc)
        raise

    logger.info("Found %d idle/underutilised RDS instance(s)", len(findings))
    return findings


# ---------------------------------------------------------------------------
# Lambda
# ---------------------------------------------------------------------------

def find_idle_lambda_functions(lambda_client, cw_client, days=30, dry_run=False):
    """Return Lambda functions with zero invocations in the last *days* days.

    Returns
    -------
    list of dicts with keys:
        function_name, runtime, last_modified, reason, recommendation
    """
    if dry_run:
        logger.info(
            "[DRY-RUN] Would call lambda.list_functions + cloudwatch.get_metric_statistics "
            "(lookback=%d days)", days,
        )
        return []

    findings = []
    try:
        paginator = lambda_client.get_paginator("list_functions")
        for page in paginator.paginate():
            for fn in page.get("Functions", []):
                fn_name = fn["FunctionName"]
                invocations = _get_average_metric(
                    cw_client,
                    "AWS/Lambda",
                    "Invocations",
                    [{"Name": "FunctionName", "Value": fn_name}],
                    days,
                )
                if invocations is None or invocations == 0:
                    findings.append({
                        "function_name": fn_name,
                        "runtime": fn.get("Runtime", ""),
                        "last_modified": fn.get("LastModified", ""),
                        "reason": f"Zero invocations in the last {days} days",
                        "recommendation": "Review and delete if no longer needed",
                    })

    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to scan Lambda functions: %s", exc)
        raise

    logger.info("Found %d idle Lambda function(s)", len(findings))
    return findings


# ---------------------------------------------------------------------------
# Load Balancers
# ---------------------------------------------------------------------------

def find_idle_load_balancers(elbv2_client, dry_run=False):
    """Return Application / Network Load Balancers that have no healthy targets.

    Returns
    -------
    list of dicts with keys:
        load_balancer_arn, name, type, state, reason, recommendation
    """
    if dry_run:
        logger.info(
            "[DRY-RUN] Would call elbv2.describe_load_balancers + describe_target_groups "
            "+ describe_target_health"
        )
        return []

    findings = []
    try:
        lb_paginator = elbv2_client.get_paginator("describe_load_balancers")
        for lb_page in lb_paginator.paginate():
            for lb in lb_page.get("LoadBalancers", []):
                lb_arn = lb["LoadBalancerArn"]
                lb_name = lb["LoadBalancerName"]
                lb_type = lb.get("Type", "")
                lb_state = lb.get("State", {}).get("Code", "")

                tg_paginator = elbv2_client.get_paginator("describe_target_groups")
                total_healthy = 0
                for tg_page in tg_paginator.paginate(LoadBalancerArn=lb_arn):
                    for tg in tg_page.get("TargetGroups", []):
                        health = elbv2_client.describe_target_health(
                            TargetGroupArn=tg["TargetGroupArn"]
                        )
                        healthy = sum(
                            1 for t in health.get("TargetHealthDescriptions", [])
                            if t.get("TargetHealth", {}).get("State") == "healthy"
                        )
                        total_healthy += healthy

                if total_healthy == 0:
                    findings.append({
                        "load_balancer_arn": lb_arn,
                        "name": lb_name,
                        "type": lb_type,
                        "state": lb_state,
                        "reason": "No healthy targets registered",
                        "recommendation": "Delete the load balancer if no targets are expected",
                    })

    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to scan load balancers: %s", exc)
        raise

    logger.info("Found %d idle load balancer(s)", len(findings))
    return findings


# ---------------------------------------------------------------------------
# NAT Gateways
# ---------------------------------------------------------------------------

def find_idle_nat_gateways(ec2_client, cw_client, days=_DEFAULT_IDLE_DAYS, dry_run=False):
    """Return NAT Gateways with near-zero bytes processed in the last *days* days.

    Returns
    -------
    list of dicts with keys:
        nat_gateway_id, vpc_id, state, bytes_out_total,
        estimated_monthly_waste_usd, reason, recommendation
    """
    if dry_run:
        logger.info(
            "[DRY-RUN] Would call ec2.describe_nat_gateways + cloudwatch.get_metric_statistics"
        )
        return []

    findings = []
    nat_est = estimate_nat_gateway_monthly()
    monthly_idle_cost = nat_est["hourly_cost_usd"]

    try:
        paginator = ec2_client.get_paginator("describe_nat_gateways")
        for page in paginator.paginate(
            Filters=[{"Name": "state", "Values": ["available"]}]
        ):
            for ngw in page.get("NatGateways", []):
                ngw_id = ngw["NatGatewayId"]
                vpc_id = ngw.get("VpcId", "")

                bytes_out = _get_average_metric(
                    cw_client,
                    "AWS/NATGateway",
                    "BytesOutToDestination",
                    [{"Name": "NatGatewayId", "Value": ngw_id}],
                    days,
                )

                if bytes_out is None or bytes_out == 0:
                    findings.append({
                        "nat_gateway_id": ngw_id,
                        "vpc_id": vpc_id,
                        "state": ngw.get("State", ""),
                        "bytes_out_total": bytes_out,
                        "estimated_monthly_waste_usd": monthly_idle_cost,
                        "reason": f"No bytes processed in the last {days} days",
                        "recommendation": "Delete the NAT Gateway if traffic is no longer expected",
                    })

    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to scan NAT Gateways: %s", exc)
        raise

    logger.info("Found %d idle NAT Gateway(s)", len(findings))
    return findings


# ---------------------------------------------------------------------------
# Aggregate helper
# ---------------------------------------------------------------------------

def find_all_idle_resources(ec2_client, rds_client, lambda_client,
                             elbv2_client, cw_client,
                             cpu_threshold=_DEFAULT_CPU_THRESHOLD,
                             idle_days=_DEFAULT_IDLE_DAYS,
                             snapshot_age_days=_DEFAULT_SNAPSHOT_AGE_DAYS,
                             dry_run=False):
    """Run all idle-resource checks and return a combined findings dict.

    Returns
    -------
    dict with keys: ec2, ebs_volumes, elastic_ips, snapshots,
                    rds, lambda, load_balancers, nat_gateways
    """
    return {
        "ec2": find_idle_ec2_instances(ec2_client, cw_client, cpu_threshold, idle_days, dry_run),
        "ebs_volumes": find_unattached_ebs_volumes(ec2_client, dry_run),
        "elastic_ips": find_unused_elastic_ips(ec2_client, dry_run),
        "snapshots": find_old_snapshots(ec2_client, snapshot_age_days, dry_run),
        "rds": find_idle_rds_instances(rds_client, cw_client, cpu_threshold, idle_days, dry_run),
        "lambda": find_idle_lambda_functions(lambda_client, cw_client, idle_days, dry_run),
        "load_balancers": find_idle_load_balancers(elbv2_client, dry_run),
        "nat_gateways": find_idle_nat_gateways(ec2_client, cw_client, idle_days, dry_run),
    }
