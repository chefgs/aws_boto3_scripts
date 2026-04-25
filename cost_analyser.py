#!/usr/bin/env python3
"""AWS Cost Analyser — unified CLI entry-point.

Sub-commands
------------
breakdown   Live cost breakdown by service (Cost Explorer)
estimate    On-demand price estimation (no resources created)
idle        Detect idle / underutilised resources
tags        Cost allocation tag analysis
budgets     Budget status and anomaly awareness

Common flags (all sub-commands)
--------------------------------
--profile   AWS profile name
--region    AWS region (default: us-east-1)
--dry-run   Preview actions without making real API calls
--output    Output format: table | json | csv  (default: table)

Examples
--------
# Live cost breakdown for the current month, top 10 services:
python cost_analyser.py breakdown

# Daily breakdown for a custom range, grouped by 'team' tag:
python cost_analyser.py breakdown --since 2024-01-01 --until 2024-01-31 \\
    --granularity DAILY --tag team

# Estimate cost for a t3.medium running 24/7:
python cost_analyser.py estimate --resource-type ec2 --instance-type t3.medium

# Find idle resources (dry-run – no API calls):
python cost_analyser.py idle --dry-run

# Show cost by 'environment' tag:
python cost_analyser.py tags --tag environment

# Show budgets and anomalies:
python cost_analyser.py budgets
"""
import logging
import sys

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_account_id, get_client

from services.cost import cost_explorer, idle_resources, pricing_estimator, report

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Argument parsers
# ---------------------------------------------------------------------------

def _common_output_args(parser):
    parser.add_argument(
        "--output",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)",
    )
    return parser


def _add_dry_run(parser):
    """Add --dry-run to a sub-command parser."""
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Preview actions without making real API calls",
    )
    return parser


def _date_range_args(parser):
    parser.add_argument("--since", default=None, metavar="YYYY-MM-DD",
                        help="Start date (inclusive)")
    parser.add_argument("--until", default=None, metavar="YYYY-MM-DD",
                        help="End date (exclusive for Cost Explorer)")
    return parser


def _build_parser():
    root = base_parser(
        "AWS Cost Analyser — identify spending and idle resources"
    )
    _common_output_args(root)

    sub = root.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    # --- breakdown ---
    p_breakdown = sub.add_parser(
        "breakdown",
        help="Live cost breakdown by service using Cost Explorer",
    )
    _date_range_args(p_breakdown)
    _common_output_args(p_breakdown)
    _add_dry_run(p_breakdown)
    p_breakdown.add_argument(
        "--granularity",
        choices=["MONTHLY", "DAILY"],
        default="MONTHLY",
        help="Time granularity (default: MONTHLY)",
    )
    p_breakdown.add_argument(
        "--tag",
        default=None,
        metavar="TAG_KEY",
        help="Add a secondary GROUP BY for this tag key",
    )
    p_breakdown.add_argument(
        "--top",
        type=int,
        default=10,
        metavar="N",
        help="Show top-N services by cost (default: 10)",
    )

    # --- estimate ---
    p_estimate = sub.add_parser(
        "estimate",
        help="Estimate monthly cost for a resource spec (no resources created)",
    )
    _common_output_args(p_estimate)
    _add_dry_run(p_estimate)
    p_estimate.add_argument(
        "--resource-type",
        required=True,
        choices=["ec2", "rds", "nat_gateway", "ebs", "lambda"],
        dest="resource_type",
        help="Type of resource to estimate",
    )
    p_estimate.add_argument("--instance-type", dest="instance_type",
                             help="EC2 instance type (e.g. t3.medium)")
    p_estimate.add_argument("--os", default="linux",
                             help="OS for EC2 pricing: linux or windows (default: linux)")
    p_estimate.add_argument("--hours", type=float, default=730,
                             help="Hours per month (default: 730 = 24×7)")
    p_estimate.add_argument("--db-instance-class", dest="db_instance_class",
                             help="RDS DB instance class (e.g. db.t3.medium)")
    p_estimate.add_argument("--multi-az", action="store_true", dest="multi_az",
                             help="RDS Multi-AZ deployment")
    p_estimate.add_argument("--gb-processed", type=float, default=0, dest="gb_processed",
                             help="NAT Gateway GB processed per month")
    p_estimate.add_argument("--volume-type", dest="volume_type",
                             help="EBS volume type: gp2, gp3, io1, st1, sc1")
    p_estimate.add_argument("--size-gb", type=float, dest="size_gb",
                             help="EBS volume size in GB")
    p_estimate.add_argument("--monthly-requests", type=int, dest="monthly_requests",
                             help="Lambda monthly invocation count")
    p_estimate.add_argument("--avg-duration-ms", type=float, dest="avg_duration_ms",
                             help="Lambda average execution duration in ms")
    p_estimate.add_argument("--memory-mb", type=int, dest="memory_mb",
                             help="Lambda configured memory in MB")

    # --- idle ---
    p_idle = sub.add_parser(
        "idle",
        help="Detect idle / underutilised resources",
    )
    _common_output_args(p_idle)
    _add_dry_run(p_idle)
    p_idle.add_argument(
        "--cpu-threshold",
        type=float,
        default=5.0,
        dest="cpu_threshold",
        metavar="PCT",
        help="Average CPU %% below which an instance is considered idle (default: 5.0)",
    )
    p_idle.add_argument(
        "--idle-days",
        type=int,
        default=14,
        dest="idle_days",
        metavar="N",
        help="Lookback window in days for CloudWatch metrics (default: 14)",
    )
    p_idle.add_argument(
        "--snapshot-age",
        type=int,
        default=90,
        dest="snapshot_age_days",
        metavar="N",
        help="Flag snapshots older than N days (default: 90)",
    )

    # --- tags ---
    p_tags = sub.add_parser(
        "tags",
        help="Cost allocation tag analysis",
    )
    _date_range_args(p_tags)
    _common_output_args(p_tags)
    _add_dry_run(p_tags)
    p_tags.add_argument(
        "--tag",
        default=None,
        metavar="TAG_KEY",
        help="Show spend grouped by this tag key (e.g. team, environment)",
    )

    # --- budgets ---
    p_budgets = sub.add_parser(
        "budgets",
        help="Show AWS Budgets status and recent cost anomalies",
    )
    _date_range_args(p_budgets)
    _common_output_args(p_budgets)
    _add_dry_run(p_budgets)

    return root


# ---------------------------------------------------------------------------
# Sub-command handlers
# ---------------------------------------------------------------------------

def _cmd_breakdown(args):
    ce = get_client("ce", args.profile, "us-east-1")
    rows = cost_explorer.get_cost_breakdown(
        ce,
        start=args.since,
        end=args.until,
        granularity=args.granularity,
        group_by_tag=args.tag,
        top_n=args.top,
        dry_run=args.dry_run,
    )
    if not rows:
        print("No cost data returned.")
        return

    headers = ["Period", "Service", "Tag Value", "Amount (USD)", "Unit"]
    data = [
        {
            "Period": r["period_start"],
            "Service": r["service"],
            "Tag Value": r.get("tag_value") or "",
            "Amount (USD)": f"{r['amount']:.4f}",
            "Unit": r["unit"],
        }
        for r in rows
    ]
    report.print_report(data, headers, args.output)


def _cmd_estimate(args):
    spec = {"resource_type": args.resource_type}

    if args.resource_type == "ec2":
        if not args.instance_type:
            print("--instance-type is required for ec2 estimation", file=sys.stderr)
            sys.exit(1)
        spec["instance_type"] = args.instance_type
        spec["os"] = args.os
        spec["hours"] = args.hours

    elif args.resource_type == "rds":
        if not args.db_instance_class:
            print("--db-instance-class is required for rds estimation", file=sys.stderr)
            sys.exit(1)
        spec["db_instance_class"] = args.db_instance_class
        spec["multi_az"] = args.multi_az
        spec["hours"] = args.hours

    elif args.resource_type == "nat_gateway":
        spec["hours"] = args.hours
        spec["gb_processed"] = args.gb_processed

    elif args.resource_type == "ebs":
        if not args.volume_type or args.size_gb is None:
            print("--volume-type and --size-gb are required for ebs estimation", file=sys.stderr)
            sys.exit(1)
        spec["volume_type"] = args.volume_type
        spec["size_gb"] = args.size_gb

    elif args.resource_type == "lambda":
        if None in (args.monthly_requests, args.avg_duration_ms, args.memory_mb):
            print(
                "--monthly-requests, --avg-duration-ms and --memory-mb are required "
                "for lambda estimation",
                file=sys.stderr,
            )
            sys.exit(1)
        spec["monthly_requests"] = args.monthly_requests
        spec["avg_duration_ms"] = args.avg_duration_ms
        spec["memory_mb"] = args.memory_mb

    result = pricing_estimator.estimate_from_spec(spec, dry_run=args.dry_run)
    if result is None:
        print("Could not compute estimate — check your arguments.", file=sys.stderr)
        sys.exit(1)

    if args.output == "json":
        print(report.format_json(result))
    else:
        headers = list(result.keys())
        rows = [[result[k] for k in headers]]
        if args.output == "csv":
            print(report.format_csv(rows, headers))
        else:
            print(report.format_table(rows, headers))


def _cmd_idle(args):
    ec2 = get_client("ec2", args.profile, args.region)
    rds = get_client("rds", args.profile, args.region)
    lmb = get_client("lambda", args.profile, args.region)
    elb = get_client("elbv2", args.profile, args.region)
    cw = get_client("cloudwatch", args.profile, args.region)

    findings = idle_resources.find_all_idle_resources(
        ec2_client=ec2,
        rds_client=rds,
        lambda_client=lmb,
        elbv2_client=elb,
        cw_client=cw,
        cpu_threshold=args.cpu_threshold,
        idle_days=args.idle_days,
        snapshot_age_days=args.snapshot_age_days,
        dry_run=args.dry_run,
    )
    report.print_idle_report(findings, args.output)


def _cmd_tags(args):
    ce = get_client("ce", args.profile, "us-east-1")

    print("\n=== ACTIVE COST ALLOCATION TAGS ===")
    active_tags = cost_explorer.list_cost_allocation_tags(ce, dry_run=args.dry_run)
    if active_tags:
        for tag in active_tags:
            print(f"  • {tag}")
    else:
        print("  (none active or dry-run)")

    if args.tag:
        print(f"\n=== SPEND BY TAG: {args.tag} ===")
        rows = cost_explorer.get_tag_spend(
            ce, args.tag, start=args.since, end=args.until, dry_run=args.dry_run
        )
        if rows:
            headers = ["Tag Value", "Amount (USD)", "Unit"]
            data = [
                {
                    "Tag Value": r["tag_value"],
                    "Amount (USD)": f"{r['amount']:.4f}",
                    "Unit": r["unit"],
                }
                for r in rows
            ]
            report.print_report(data, headers, args.output)
        else:
            print("  (no data returned)")


def _cmd_budgets(args):
    ce = get_client("ce", args.profile, "us-east-1")
    budgets_client = get_client("budgets", args.profile, "us-east-1")
    account_id = get_account_id(args.profile, args.region)

    print("\n=== AWS BUDGETS ===")
    budget_list = cost_explorer.get_budgets(budgets_client, account_id, dry_run=args.dry_run)
    if budget_list:
        headers = ["Name", "Type", "Limit (USD)", "Actual (USD)", "Forecast (USD)", "Status"]
        data = []
        for b in budget_list:
            pct = (
                b["actual_spend"] / b["limit_amount"] * 100
                if b["limit_amount"] > 0 else 0.0
            )
            status = "⚠ OVER" if b["actual_spend"] > b["limit_amount"] else (
                "⚠ AT RISK" if b["forecasted_spend"] > b["limit_amount"] else "OK"
            )
            data.append({
                "Name": b["name"],
                "Type": b["budget_type"],
                "Limit (USD)": f"{b['limit_amount']:.2f}",
                "Actual (USD)": f"{b['actual_spend']:.2f} ({pct:.0f}%)",
                "Forecast (USD)": f"{b['forecasted_spend']:.2f}",
                "Status": status,
            })
        report.print_report(data, headers, args.output)
    else:
        print("  (no budgets found or dry-run)")

    print("\n=== COST ANOMALIES ===")
    anomalies = cost_explorer.get_anomalies(
        ce, start=args.since, end=args.until, dry_run=args.dry_run
    )
    if anomalies:
        headers = ["Anomaly ID", "Start Date", "Impact (USD)", "Service"]
        data = [
            {
                "Anomaly ID": a.get("AnomalyId", ""),
                "Start Date": a.get("AnomalyStartDate", ""),
                "Impact (USD)": f"{a.get('Impact', {}).get('TotalActualSpend', 0):.2f}",
                "Service": str(a.get("RootCauses", [{}])[0].get("Service", "")),
            }
            for a in anomalies
        ]
        report.print_report(data, headers, args.output)
    else:
        print("  (no anomalies found or dry-run)")


# ---------------------------------------------------------------------------
# Entry-point
# ---------------------------------------------------------------------------

_COMMANDS = {
    "breakdown": _cmd_breakdown,
    "estimate": _cmd_estimate,
    "idle": _cmd_idle,
    "tags": _cmd_tags,
    "budgets": _cmd_budgets,
}


def main(argv=None):
    setup_logging()
    parser = _build_parser()
    args = parser.parse_args(argv)
    handler = _COMMANDS.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)
    handler(args)


if __name__ == "__main__":
    main()
