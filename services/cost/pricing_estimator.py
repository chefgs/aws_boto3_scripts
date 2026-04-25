"""On-demand price estimation via the AWS Pricing API (and static fallback)."""
import json
import logging
import os

import botocore.exceptions

logger = logging.getLogger(__name__)

_STATIC_PRICES_PATH = os.path.join(os.path.dirname(__file__), "data", "pricing_static.json")
_HOURS_PER_MONTH = 730


def load_static_prices():
    """Load the bundled static price snapshot from disk.

    Returns
    -------
    dict  (the full parsed JSON)
    """
    with open(_STATIC_PRICES_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def get_ec2_hourly_price(pricing_client, instance_type, os_name="Linux",
                         region="us-east-1", dry_run=False):
    """Look up the current on-demand hourly price for an EC2 instance type.

    Falls back to the static price file when *dry_run* is True or when the
    Pricing API call fails to return a usable result.

    Parameters
    ----------
    pricing_client : boto3 client for 'pricing' (must use us-east-1 or ap-south-1 endpoint)
    instance_type  : e.g. 't3.medium'
    os_name        : 'Linux' or 'Windows'
    region         : AWS region display name passed to the filter
    dry_run        : skip the live API call and use the static snapshot instead

    Returns
    -------
    float  hourly price in USD, or None if not found
    """
    os_key = os_name.lower()

    if dry_run:
        logger.info(
            "[DRY-RUN] Using static price for EC2 %s / %s", instance_type, os_name
        )
        prices = load_static_prices()
        return prices.get("ec2", {}).get(instance_type, {}).get(os_key)

    # AWS Pricing API region display names differ from API region identifiers
    region_display_map = {
        "us-east-1": "US East (N. Virginia)",
        "us-east-2": "US East (Ohio)",
        "us-west-1": "US West (N. California)",
        "us-west-2": "US West (Oregon)",
        "eu-west-1": "Europe (Ireland)",
        "eu-central-1": "Europe (Frankfurt)",
        "ap-southeast-1": "Asia Pacific (Singapore)",
        "ap-southeast-2": "Asia Pacific (Sydney)",
        "ap-northeast-1": "Asia Pacific (Tokyo)",
        "ap-south-1": "Asia Pacific (Mumbai)",
        "sa-east-1": "South America (Sao Paulo)",
    }
    region_display = region_display_map.get(region, "US East (N. Virginia)")

    try:
        resp = pricing_client.get_products(
            ServiceCode="AmazonEC2",
            Filters=[
                {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
                {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": os_name},
                {"Type": "TERM_MATCH", "Field": "location", "Value": region_display},
                {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
                {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"},
                {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
            ],
            MaxResults=5,
        )
        price_list = resp.get("PriceList", [])
        if not price_list:
            logger.warning(
                "No pricing data returned for %s / %s — using static fallback",
                instance_type, os_name,
            )
            prices = load_static_prices()
            return prices.get("ec2", {}).get(instance_type, {}).get(os_key)

        product = json.loads(price_list[0])
        on_demand = product.get("terms", {}).get("OnDemand", {})
        for term in on_demand.values():
            for dim in term.get("priceDimensions", {}).values():
                price_per_unit = float(dim["pricePerUnit"].get("USD", 0))
                if price_per_unit > 0:
                    return price_per_unit
        return None

    except botocore.exceptions.ClientError as exc:
        logger.warning("Pricing API error — falling back to static prices: %s", exc)
        prices = load_static_prices()
        return prices.get("ec2", {}).get(instance_type, {}).get(os_key)


def estimate_ec2_monthly(instance_type, hourly_price, hours=_HOURS_PER_MONTH):
    """Return estimated monthly cost for an EC2 instance.

    Parameters
    ----------
    instance_type : str (informational)
    hourly_price  : float (USD/hour)
    hours         : hours per month (default: 730)

    Returns
    -------
    dict with keys: instance_type, hourly_price, hours, monthly_cost_usd
    """
    monthly = hourly_price * hours
    logger.info(
        "EC2 estimate: %s @ $%.4f/hr × %d hrs = $%.2f/month",
        instance_type, hourly_price, hours, monthly,
    )
    return {
        "instance_type": instance_type,
        "hourly_price_usd": hourly_price,
        "hours": hours,
        "monthly_cost_usd": monthly,
    }


def estimate_rds_monthly(db_instance_class, multi_az=False, hours=_HOURS_PER_MONTH,
                         dry_run=False):
    """Estimate monthly cost for an RDS instance using the static price table.

    Returns
    -------
    dict with keys: db_instance_class, multi_az, hourly_price, hours, monthly_cost_usd
    """
    prices = load_static_prices()
    az_key = "multi_az" if multi_az else "single"
    hourly = prices.get("rds", {}).get(db_instance_class, {}).get(az_key)

    if hourly is None:
        logger.warning("No static price found for RDS %s (multi_az=%s)", db_instance_class, multi_az)
        return None

    monthly = hourly * hours
    if dry_run:
        logger.info(
            "[DRY-RUN] RDS estimate: %s (multi_az=%s) @ $%.4f/hr × %d hrs = $%.2f/month",
            db_instance_class, multi_az, hourly, hours, monthly,
        )
    return {
        "db_instance_class": db_instance_class,
        "multi_az": multi_az,
        "hourly_price_usd": hourly,
        "hours": hours,
        "monthly_cost_usd": monthly,
    }


def estimate_nat_gateway_monthly(hours=_HOURS_PER_MONTH, gb_processed=0, dry_run=False):
    """Estimate monthly cost for a NAT Gateway.

    Returns
    -------
    dict with keys: hourly_cost, data_cost, monthly_cost_usd
    """
    prices = load_static_prices()
    nat = prices.get("nat_gateway", {})
    hourly_cost = nat.get("hourly_usd", 0.045) * hours
    data_cost = nat.get("per_gb_usd", 0.045) * gb_processed
    monthly = hourly_cost + data_cost

    if dry_run:
        logger.info(
            "[DRY-RUN] NAT GW estimate: hourly=$%.2f + data=$%.2f = $%.2f/month",
            hourly_cost, data_cost, monthly,
        )
    return {
        "hourly_cost_usd": hourly_cost,
        "data_transfer_cost_usd": data_cost,
        "monthly_cost_usd": monthly,
    }


def estimate_ebs_monthly(volume_type, size_gb, dry_run=False):
    """Estimate monthly cost for an EBS volume.

    Parameters
    ----------
    volume_type : 'gp2', 'gp3', 'io1', 'st1', 'sc1'
    size_gb     : int/float

    Returns
    -------
    dict with keys: volume_type, size_gb, monthly_cost_usd
    """
    prices = load_static_prices()
    key = f"{volume_type}_per_gb_month"
    rate = prices.get("ebs", {}).get(key)
    if rate is None:
        logger.warning("No static price found for EBS volume type '%s'", volume_type)
        return None
    monthly = rate * size_gb
    if dry_run:
        logger.info(
            "[DRY-RUN] EBS estimate: %s %dGB @ $%.4f/GB/month = $%.2f/month",
            volume_type, size_gb, rate, monthly,
        )
    return {
        "volume_type": volume_type,
        "size_gb": size_gb,
        "rate_per_gb_month": rate,
        "monthly_cost_usd": monthly,
    }


def estimate_lambda_monthly(monthly_requests, avg_duration_ms, memory_mb, dry_run=False):
    """Estimate monthly cost for a Lambda function.

    Parameters
    ----------
    monthly_requests  : int
    avg_duration_ms   : float (average execution duration in milliseconds)
    memory_mb         : int (configured memory in MB)

    Returns
    -------
    dict with keys: request_cost_usd, compute_cost_usd, monthly_cost_usd
    """
    prices = load_static_prices()
    lp = prices.get("lambda", {})
    request_cost = (monthly_requests / 1_000_000) * lp.get("per_1m_requests_usd", 0.20)
    gb_seconds = (avg_duration_ms / 1000) * (memory_mb / 1024) * monthly_requests
    compute_cost = gb_seconds * lp.get("per_gb_second_usd", 0.0000166667)
    monthly = request_cost + compute_cost
    if dry_run:
        logger.info(
            "[DRY-RUN] Lambda estimate: requests=$%.4f + compute=$%.4f = $%.4f/month",
            request_cost, compute_cost, monthly,
        )
    return {
        "monthly_requests": monthly_requests,
        "avg_duration_ms": avg_duration_ms,
        "memory_mb": memory_mb,
        "request_cost_usd": request_cost,
        "compute_cost_usd": compute_cost,
        "monthly_cost_usd": monthly,
    }


def estimate_from_spec(spec, dry_run=False):
    """Estimate monthly cost from a resource specification dict.

    The *spec* dict must contain at minimum a 'resource_type' key.
    Supported types and their required keys:

    * ``ec2``          — instance_type, [os, hours]
    * ``rds``          — db_instance_class, [multi_az, hours]
    * ``nat_gateway``  — [hours, gb_processed]
    * ``ebs``          — volume_type, size_gb
    * ``lambda``       — monthly_requests, avg_duration_ms, memory_mb

    Returns
    -------
    dict  with at least a 'monthly_cost_usd' key, or None on unknown type
    """
    resource_type = spec.get("resource_type", "").lower()

    if resource_type == "ec2":
        prices = load_static_prices()
        os_name = spec.get("os", "linux")
        instance_type = spec["instance_type"]
        hourly = prices.get("ec2", {}).get(instance_type, {}).get(os_name)
        if hourly is None:
            logger.warning("No static price for EC2 %s/%s", instance_type, os_name)
            return None
        return estimate_ec2_monthly(instance_type, hourly, spec.get("hours", _HOURS_PER_MONTH))

    if resource_type == "rds":
        return estimate_rds_monthly(
            spec["db_instance_class"],
            multi_az=spec.get("multi_az", False),
            hours=spec.get("hours", _HOURS_PER_MONTH),
            dry_run=dry_run,
        )

    if resource_type == "nat_gateway":
        return estimate_nat_gateway_monthly(
            hours=spec.get("hours", _HOURS_PER_MONTH),
            gb_processed=spec.get("gb_processed", 0),
            dry_run=dry_run,
        )

    if resource_type == "ebs":
        return estimate_ebs_monthly(spec["volume_type"], spec["size_gb"], dry_run=dry_run)

    if resource_type == "lambda":
        return estimate_lambda_monthly(
            spec["monthly_requests"],
            spec["avg_duration_ms"],
            spec["memory_mb"],
            dry_run=dry_run,
        )

    logger.warning("Unknown resource_type '%s' in spec", resource_type)
    return None
