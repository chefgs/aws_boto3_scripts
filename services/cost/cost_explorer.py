"""Live billing data via AWS Cost Explorer API."""
import logging
from datetime import date, timedelta

import botocore.exceptions

logger = logging.getLogger(__name__)

_HOURS_PER_MONTH = 730


def _month_range():
    """Return (start, end) strings for the current calendar month (YYYY-MM-DD)."""
    today = date.today()
    start = today.replace(day=1).isoformat()
    # Cost Explorer end date is exclusive, so use tomorrow or today+1
    end = today.isoformat()
    if start == end:
        # First day of month: look back to previous month
        first = today.replace(day=1)
        prev_last = first - timedelta(days=1)
        start = prev_last.replace(day=1).isoformat()
        end = first.isoformat()
    return start, end


def get_cost_breakdown(ce_client, start=None, end=None, granularity="MONTHLY",
                       group_by_tag=None, top_n=10, dry_run=False):
    """Return cost grouped by SERVICE (and optionally a tag) for the given period.

    Parameters
    ----------
    ce_client : boto3 client for 'ce'
    start, end : ISO-8601 date strings (end is exclusive). Default: current month.
    granularity : 'DAILY' or 'MONTHLY'
    group_by_tag : optional tag key to add a second GROUP BY dimension
    top_n : keep only the top-N services by total cost
    dry_run : if True, log the intended call and return an empty list

    Returns
    -------
    list of dicts with keys: period_start, service, tag_value, amount, unit
    """
    if start is None or end is None:
        start, end = _month_range()

    group_by = [{"Type": "DIMENSION", "Key": "SERVICE"}]
    if group_by_tag:
        group_by.append({"Type": "TAG", "Key": group_by_tag})

    if dry_run:
        logger.info(
            "[DRY-RUN] Would call ce.get_cost_and_usage("
            "TimePeriod={'Start': '%s', 'End': '%s'}, Granularity='%s', GroupBy=%s)",
            start, end, granularity, group_by,
        )
        return []

    try:
        paginator = ce_client.get_paginator("get_cost_and_usage")
        rows = []
        for page in paginator.paginate(
            TimePeriod={"Start": start, "End": end},
            Granularity=granularity,
            Metrics=["UnblendedCost"],
            GroupBy=group_by,
        ):
            for result in page.get("ResultsByTime", []):
                period_start = result["TimePeriod"]["Start"]
                for group in result.get("Groups", []):
                    keys = group["Keys"]
                    service = keys[0]
                    tag_value = keys[1] if len(keys) > 1 else None
                    amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
                    unit = group["Metrics"]["UnblendedCost"]["Unit"]
                    rows.append({
                        "period_start": period_start,
                        "service": service,
                        "tag_value": tag_value,
                        "amount": amount,
                        "unit": unit,
                    })

        # Aggregate totals per service for top-N filtering
        totals = {}
        for row in rows:
            totals[row["service"]] = totals.get(row["service"], 0.0) + row["amount"]
        top_services = {
            svc for svc, _ in sorted(totals.items(), key=lambda x: x[1], reverse=True)[:top_n]
        }
        filtered = [r for r in rows if r["service"] in top_services]
        logger.info(
            "Cost breakdown: %d rows returned for %s → %s (top %d services)",
            len(filtered), start, end, top_n,
        )
        return filtered

    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to get cost breakdown: %s", exc)
        raise


def get_tag_spend(ce_client, tag_key, start=None, end=None, dry_run=False):
    """Return cost grouped by a specific tag key for the given period.

    Returns
    -------
    list of dicts with keys: tag_value, amount, unit
    """
    if start is None or end is None:
        start, end = _month_range()

    if dry_run:
        logger.info(
            "[DRY-RUN] Would call ce.get_cost_and_usage(GroupBy TAG:%s, %s → %s)",
            tag_key, start, end,
        )
        return []

    try:
        paginator = ce_client.get_paginator("get_cost_and_usage")
        totals = {}
        unit = "USD"
        for page in paginator.paginate(
            TimePeriod={"Start": start, "End": end},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "TAG", "Key": tag_key}],
        ):
            for result in page.get("ResultsByTime", []):
                for group in result.get("Groups", []):
                    tag_value = group["Keys"][0] if group["Keys"] else ""
                    amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
                    unit = group["Metrics"]["UnblendedCost"]["Unit"]
                    totals[tag_value] = totals.get(tag_value, 0.0) + amount

        rows = [
            {"tag_value": tv, "amount": amt, "unit": unit}
            for tv, amt in sorted(totals.items(), key=lambda x: x[1], reverse=True)
        ]
        logger.info("Tag spend for '%s': %d distinct values", tag_key, len(rows))
        return rows

    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to get tag spend for '%s': %s", tag_key, exc)
        raise


def list_cost_allocation_tags(ce_client, dry_run=False):
    """Return active cost allocation tag keys.

    Returns
    -------
    list of tag key strings
    """
    if dry_run:
        logger.info("[DRY-RUN] Would call ce.list_cost_allocation_tags(Status='Active')")
        return []

    try:
        tags = []
        kwargs = {"Status": "Active", "MaxResults": 100}
        while True:
            resp = ce_client.list_cost_allocation_tags(**kwargs)
            for tag in resp.get("CostAllocationTags", []):
                tags.append(tag["TagKey"])
                logger.info("Cost allocation tag: %s (type=%s)", tag["TagKey"], tag["Type"])
            next_token = resp.get("NextToken")
            if not next_token:
                break
            kwargs["NextToken"] = next_token
        return tags

    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list cost allocation tags: %s", exc)
        raise


def get_anomalies(ce_client, start=None, end=None, dry_run=False):
    """Return recent cost anomalies detected by Cost Explorer.

    Returns
    -------
    list of anomaly dicts (AnomalyId, AnomalyStartDate, Impact, RootCauses)
    """
    if start is None or end is None:
        today = date.today()
        end = today.isoformat()
        start = (today - timedelta(days=90)).isoformat()

    if dry_run:
        logger.info(
            "[DRY-RUN] Would call ce.get_anomalies(DateInterval={'StartDate': '%s', 'EndDate': '%s'})",
            start, end,
        )
        return []

    try:
        resp = ce_client.get_anomalies(
            DateInterval={"StartDate": start, "EndDate": end},
            MaxResults=100,
        )
        anomalies = resp.get("Anomalies", [])
        logger.info("Found %d anomalies between %s and %s", len(anomalies), start, end)
        return anomalies

    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to get anomalies: %s", exc)
        raise


def get_budgets(budgets_client, account_id, dry_run=False):
    """Return AWS Budgets for the given account with current vs. limit.

    Returns
    -------
    list of dicts with keys: name, budget_type, limit_amount, limit_unit,
                              actual_spend, forecasted_spend
    """
    if dry_run:
        logger.info("[DRY-RUN] Would call budgets.describe_budgets(AccountId='%s')", account_id)
        return []

    try:
        paginator = budgets_client.get_paginator("describe_budgets")
        result = []
        for page in paginator.paginate(AccountId=account_id):
            for budget in page.get("Budgets", []):
                calc_spend = budget.get("CalculatedSpend", {})
                actual = calc_spend.get("ActualSpend", {})
                forecast = calc_spend.get("ForecastedSpend", {})
                entry = {
                    "name": budget["BudgetName"],
                    "budget_type": budget["BudgetType"],
                    "limit_amount": float(budget["BudgetLimit"]["Amount"]),
                    "limit_unit": budget["BudgetLimit"]["Unit"],
                    "actual_spend": float(actual.get("Amount", 0)),
                    "forecasted_spend": float(forecast.get("Amount", 0)),
                }
                pct = (
                    entry["actual_spend"] / entry["limit_amount"] * 100
                    if entry["limit_amount"] > 0
                    else 0.0
                )
                logger.info(
                    "Budget '%s': %.2f / %.2f %s (%.1f%%)",
                    entry["name"], entry["actual_spend"],
                    entry["limit_amount"], entry["limit_unit"], pct,
                )
                result.append(entry)
        return result

    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to describe budgets: %s", exc)
        raise
