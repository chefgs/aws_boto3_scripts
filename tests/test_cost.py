"""Unit tests for the AWS Cost Calculator / Analyser module."""
import json
import os
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import boto3
import pytest
from moto import mock_aws

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def _load_fixture(name):
    with open(os.path.join(FIXTURES_DIR, name), encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# pricing_estimator
# ---------------------------------------------------------------------------

class TestLoadStaticPrices:
    def test_loads_without_error(self):
        from services.cost.pricing_estimator import load_static_prices
        prices = load_static_prices()
        assert "ec2" in prices
        assert "rds" in prices
        assert "lambda" in prices

    def test_ec2_t3_medium_present(self):
        from services.cost.pricing_estimator import load_static_prices
        prices = load_static_prices()
        assert prices["ec2"]["t3.medium"]["linux"] == pytest.approx(0.0416)


class TestEstimateEc2Monthly:
    def test_basic_calculation(self):
        from services.cost.pricing_estimator import estimate_ec2_monthly
        result = estimate_ec2_monthly("t3.medium", hourly_price=0.0416, hours=730)
        assert result["monthly_cost_usd"] == pytest.approx(0.0416 * 730)
        assert result["instance_type"] == "t3.medium"

    def test_custom_hours(self):
        from services.cost.pricing_estimator import estimate_ec2_monthly
        result = estimate_ec2_monthly("t3.medium", hourly_price=0.0416, hours=100)
        assert result["monthly_cost_usd"] == pytest.approx(4.16)


class TestEstimateRdsMonthly:
    def test_single_az(self):
        from services.cost.pricing_estimator import estimate_rds_monthly
        result = estimate_rds_monthly("db.t3.micro", multi_az=False)
        assert result is not None
        assert result["monthly_cost_usd"] == pytest.approx(0.017 * 730)

    def test_multi_az_is_double(self):
        from services.cost.pricing_estimator import estimate_rds_monthly
        single = estimate_rds_monthly("db.t3.micro", multi_az=False)
        multi = estimate_rds_monthly("db.t3.micro", multi_az=True)
        assert multi["monthly_cost_usd"] == pytest.approx(single["monthly_cost_usd"] * 2)

    def test_unknown_class_returns_none(self):
        from services.cost.pricing_estimator import estimate_rds_monthly
        assert estimate_rds_monthly("db.x99.unknown") is None


class TestEstimateNatGatewayMonthly:
    def test_no_data_transfer(self):
        from services.cost.pricing_estimator import estimate_nat_gateway_monthly
        result = estimate_nat_gateway_monthly(hours=730, gb_processed=0)
        assert result["monthly_cost_usd"] == pytest.approx(0.045 * 730)
        assert result["data_transfer_cost_usd"] == pytest.approx(0.0)

    def test_with_data_transfer(self):
        from services.cost.pricing_estimator import estimate_nat_gateway_monthly
        result = estimate_nat_gateway_monthly(hours=730, gb_processed=100)
        expected = 0.045 * 730 + 0.045 * 100
        assert result["monthly_cost_usd"] == pytest.approx(expected)


class TestEstimateEbsMonthly:
    def test_gp2(self):
        from services.cost.pricing_estimator import estimate_ebs_monthly
        result = estimate_ebs_monthly("gp2", 100)
        assert result["monthly_cost_usd"] == pytest.approx(10.0)

    def test_gp3_cheaper_than_gp2(self):
        from services.cost.pricing_estimator import estimate_ebs_monthly
        gp2 = estimate_ebs_monthly("gp2", 100)
        gp3 = estimate_ebs_monthly("gp3", 100)
        assert gp3["monthly_cost_usd"] < gp2["monthly_cost_usd"]

    def test_unknown_type_returns_none(self):
        from services.cost.pricing_estimator import estimate_ebs_monthly
        assert estimate_ebs_monthly("xyztype", 100) is None


class TestEstimateLambdaMonthly:
    def test_basic(self):
        from services.cost.pricing_estimator import estimate_lambda_monthly
        result = estimate_lambda_monthly(
            monthly_requests=1_000_000,
            avg_duration_ms=200,
            memory_mb=128,
        )
        assert result["monthly_cost_usd"] > 0
        # Request cost: 1M × $0.20/1M = $0.20
        assert result["request_cost_usd"] == pytest.approx(0.20)

    def test_zero_invocations(self):
        from services.cost.pricing_estimator import estimate_lambda_monthly
        result = estimate_lambda_monthly(0, 200, 128)
        assert result["monthly_cost_usd"] == pytest.approx(0.0)


class TestEstimateFromSpec:
    def test_ec2_spec(self):
        from services.cost.pricing_estimator import estimate_from_spec
        spec = {"resource_type": "ec2", "instance_type": "t3.medium", "os": "linux"}
        result = estimate_from_spec(spec)
        assert result is not None
        assert result["monthly_cost_usd"] == pytest.approx(0.0416 * 730)

    def test_rds_spec(self):
        from services.cost.pricing_estimator import estimate_from_spec
        spec = {"resource_type": "rds", "db_instance_class": "db.t3.micro", "multi_az": False}
        result = estimate_from_spec(spec)
        assert result is not None
        assert result["monthly_cost_usd"] > 0

    def test_nat_gateway_spec(self):
        from services.cost.pricing_estimator import estimate_from_spec
        spec = {"resource_type": "nat_gateway", "gb_processed": 50}
        result = estimate_from_spec(spec)
        assert result is not None
        assert result["monthly_cost_usd"] > 0

    def test_ebs_spec(self):
        from services.cost.pricing_estimator import estimate_from_spec
        spec = {"resource_type": "ebs", "volume_type": "gp2", "size_gb": 200}
        result = estimate_from_spec(spec)
        assert result["monthly_cost_usd"] == pytest.approx(20.0)

    def test_lambda_spec(self):
        from services.cost.pricing_estimator import estimate_from_spec
        spec = {
            "resource_type": "lambda",
            "monthly_requests": 500_000,
            "avg_duration_ms": 100,
            "memory_mb": 256,
        }
        result = estimate_from_spec(spec)
        assert result is not None
        assert result["monthly_cost_usd"] >= 0

    def test_dry_run_returns_result(self):
        from services.cost.pricing_estimator import estimate_from_spec
        spec = {"resource_type": "ec2", "instance_type": "m5.large", "os": "linux"}
        result = estimate_from_spec(spec, dry_run=True)
        assert result is not None

    def test_unknown_type_returns_none(self):
        from services.cost.pricing_estimator import estimate_from_spec
        assert estimate_from_spec({"resource_type": "mystery_service"}) is None

    def test_ec2_dry_run_live_api_skipped(self):
        """estimate_from_spec uses static prices regardless of dry_run for ec2."""
        from services.cost.pricing_estimator import estimate_from_spec
        spec = {"resource_type": "ec2", "instance_type": "t3.micro", "os": "linux"}
        result = estimate_from_spec(spec, dry_run=True)
        assert result["monthly_cost_usd"] == pytest.approx(0.0104 * 730)


# ---------------------------------------------------------------------------
# pricing_estimator — get_ec2_hourly_price (dry-run path)
# ---------------------------------------------------------------------------

class TestGetEc2HourlyPriceDryRun:
    def test_dry_run_uses_static_file(self):
        from services.cost.pricing_estimator import get_ec2_hourly_price
        mock_pricing = MagicMock()
        price = get_ec2_hourly_price(mock_pricing, "t3.medium", "Linux", dry_run=True)
        assert price == pytest.approx(0.0416)
        mock_pricing.get_products.assert_not_called()

    def test_dry_run_windows(self):
        from services.cost.pricing_estimator import get_ec2_hourly_price
        mock_pricing = MagicMock()
        price = get_ec2_hourly_price(mock_pricing, "t3.medium", "Windows", dry_run=True)
        assert price == pytest.approx(0.0568)


# ---------------------------------------------------------------------------
# cost_explorer — dry-run paths (no real CE client needed)
# ---------------------------------------------------------------------------

class TestCostExplorerDryRun:
    def setup_method(self):
        self.ce = MagicMock()

    def test_get_cost_breakdown_dry_run(self):
        from services.cost.cost_explorer import get_cost_breakdown
        result = get_cost_breakdown(self.ce, dry_run=True)
        assert result == []
        self.ce.get_paginator.assert_not_called()

    def test_get_tag_spend_dry_run(self):
        from services.cost.cost_explorer import get_tag_spend
        result = get_tag_spend(self.ce, "team", dry_run=True)
        assert result == []

    def test_list_cost_allocation_tags_dry_run(self):
        from services.cost.cost_explorer import list_cost_allocation_tags
        result = list_cost_allocation_tags(self.ce, dry_run=True)
        assert result == []

    def test_get_anomalies_dry_run(self):
        from services.cost.cost_explorer import get_anomalies
        result = get_anomalies(self.ce, dry_run=True)
        assert result == []

    def test_get_budgets_dry_run(self):
        from services.cost.cost_explorer import get_budgets
        budgets_client = MagicMock()
        result = get_budgets(budgets_client, "123456789012", dry_run=True)
        assert result == []


# ---------------------------------------------------------------------------
# cost_explorer — mock-based live-path tests
# ---------------------------------------------------------------------------

class TestCostExplorerLive:
    def _make_ce_page(self, service, amount, period_start="2024-01-01"):
        return {
            "ResultsByTime": [
                {
                    "TimePeriod": {"Start": period_start, "End": "2024-01-31"},
                    "Groups": [
                        {
                            "Keys": [service],
                            "Metrics": {
                                "UnblendedCost": {"Amount": str(amount), "Unit": "USD"}
                            },
                        }
                    ],
                }
            ]
        }

    def test_get_cost_breakdown_returns_rows(self):
        from services.cost.cost_explorer import get_cost_breakdown
        ce = MagicMock()
        paginator = MagicMock()
        paginator.paginate.return_value = [
            self._make_ce_page("Amazon EC2", 50.0),
            self._make_ce_page("Amazon RDS", 20.0),
        ]
        ce.get_paginator.return_value = paginator

        rows = get_cost_breakdown(ce, start="2024-01-01", end="2024-01-31")
        assert len(rows) == 2
        services = {r["service"] for r in rows}
        assert "Amazon EC2" in services

    def test_get_cost_breakdown_top_n(self):
        from services.cost.cost_explorer import get_cost_breakdown
        ce = MagicMock()
        paginator = MagicMock()
        # Produce 5 services
        groups = [
            {
                "Keys": [f"Service-{i}"],
                "Metrics": {"UnblendedCost": {"Amount": str(float(i * 10)), "Unit": "USD"}},
            }
            for i in range(1, 6)
        ]
        paginator.paginate.return_value = [
            {
                "ResultsByTime": [
                    {
                        "TimePeriod": {"Start": "2024-01-01", "End": "2024-01-31"},
                        "Groups": groups,
                    }
                ]
            }
        ]
        ce.get_paginator.return_value = paginator

        rows = get_cost_breakdown(ce, start="2024-01-01", end="2024-01-31", top_n=3)
        returned_services = {r["service"] for r in rows}
        # Only top 3 by cost should be returned
        assert len(returned_services) <= 3

    def test_list_cost_allocation_tags_live(self):
        from services.cost.cost_explorer import list_cost_allocation_tags
        ce = MagicMock()
        ce.list_cost_allocation_tags.return_value = {
            "CostAllocationTags": [
                {"TagKey": "team", "Type": "UserDefined"},
                {"TagKey": "env", "Type": "UserDefined"},
            ]
        }
        tags = list_cost_allocation_tags(ce)
        assert tags == ["team", "env"]

    def test_get_tag_spend_live(self):
        from services.cost.cost_explorer import get_tag_spend
        ce = MagicMock()
        paginator = MagicMock()
        paginator.paginate.return_value = [
            {
                "ResultsByTime": [
                    {
                        "TimePeriod": {"Start": "2024-01-01", "End": "2024-01-31"},
                        "Groups": [
                            {
                                "Keys": ["team$backend"],
                                "Metrics": {"UnblendedCost": {"Amount": "100.0", "Unit": "USD"}},
                            },
                            {
                                "Keys": ["team$frontend"],
                                "Metrics": {"UnblendedCost": {"Amount": "40.0", "Unit": "USD"}},
                            },
                        ],
                    }
                ]
            }
        ]
        ce.get_paginator.return_value = paginator
        rows = get_tag_spend(ce, "team", start="2024-01-01", end="2024-01-31")
        assert rows[0]["tag_value"] == "team$backend"
        assert rows[0]["amount"] == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# idle_resources — EC2 (moto)
# ---------------------------------------------------------------------------

@mock_aws
class TestFindUnattachedEbs:
    def test_detects_available_volume(self):
        from services.cost.idle_resources import find_unattached_ebs_volumes
        client = boto3.client("ec2", region_name="us-east-1")
        client.create_volume(AvailabilityZone="us-east-1a", Size=20, VolumeType="gp2")
        findings = find_unattached_ebs_volumes(client)
        assert len(findings) >= 1
        assert findings[0]["state"] == "available"

    def test_dry_run_returns_empty(self):
        from services.cost.idle_resources import find_unattached_ebs_volumes
        client = boto3.client("ec2", region_name="us-east-1")
        client.create_volume(AvailabilityZone="us-east-1a", Size=50, VolumeType="gp2")
        result = find_unattached_ebs_volumes(client, dry_run=True)
        assert result == []


@mock_aws
class TestFindUnusedElasticIps:
    def test_detects_unassociated_eip(self):
        from services.cost.idle_resources import find_unused_elastic_ips
        client = boto3.client("ec2", region_name="us-east-1")
        client.allocate_address(Domain="vpc")
        findings = find_unused_elastic_ips(client)
        assert len(findings) >= 1

    def test_dry_run_returns_empty(self):
        from services.cost.idle_resources import find_unused_elastic_ips
        client = boto3.client("ec2", region_name="us-east-1")
        client.allocate_address(Domain="vpc")
        assert find_unused_elastic_ips(client, dry_run=True) == []


@mock_aws
class TestFindIdleEc2Instances:
    def test_detects_stopped_instance(self):
        from services.cost.idle_resources import find_idle_ec2_instances
        ec2 = boto3.client("ec2", region_name="us-east-1")
        cw = boto3.client("cloudwatch", region_name="us-east-1")
        resp = ec2.run_instances(ImageId="ami-12345678", MinCount=1, MaxCount=1,
                                  InstanceType="t3.medium")
        instance_id = resp["Instances"][0]["InstanceId"]
        ec2.stop_instances(InstanceIds=[instance_id])

        findings = find_idle_ec2_instances(ec2, cw)
        stopped_ids = [f["instance_id"] for f in findings if f["state"] == "stopped"]
        assert instance_id in stopped_ids

    def test_dry_run_returns_empty(self):
        from services.cost.idle_resources import find_idle_ec2_instances
        ec2 = boto3.client("ec2", region_name="us-east-1")
        cw = boto3.client("cloudwatch", region_name="us-east-1")
        ec2.run_instances(ImageId="ami-12345678", MinCount=1, MaxCount=1)
        result = find_idle_ec2_instances(ec2, cw, dry_run=True)
        assert result == []


@mock_aws
class TestFindOldSnapshots:
    def test_detects_no_snapshots_when_none_exist(self):
        from services.cost.idle_resources import find_old_snapshots
        ec2 = boto3.client("ec2", region_name="us-east-1")
        # moto snapshots created now won't be older than 90 days
        findings = find_old_snapshots(ec2, age_days=90)
        assert isinstance(findings, list)

    def test_dry_run_returns_empty(self):
        from services.cost.idle_resources import find_old_snapshots
        ec2 = boto3.client("ec2", region_name="us-east-1")
        result = find_old_snapshots(ec2, dry_run=True)
        assert result == []


# ---------------------------------------------------------------------------
# idle_resources — RDS (moto)
# ---------------------------------------------------------------------------

@mock_aws
class TestFindIdleRds:
    def test_dry_run_returns_empty(self):
        from services.cost.idle_resources import find_idle_rds_instances
        rds = boto3.client("rds", region_name="us-east-1")
        cw = boto3.client("cloudwatch", region_name="us-east-1")
        result = find_idle_rds_instances(rds, cw, dry_run=True)
        assert result == []

    def test_returns_list(self):
        from services.cost.idle_resources import find_idle_rds_instances
        rds = boto3.client("rds", region_name="us-east-1")
        cw = boto3.client("cloudwatch", region_name="us-east-1")
        findings = find_idle_rds_instances(rds, cw)
        assert isinstance(findings, list)


# ---------------------------------------------------------------------------
# idle_resources — Lambda (moto)
# ---------------------------------------------------------------------------

@mock_aws
class TestFindIdleLambda:
    def test_dry_run_returns_empty(self):
        from services.cost.idle_resources import find_idle_lambda_functions
        lmb = boto3.client("lambda", region_name="us-east-1")
        cw = boto3.client("cloudwatch", region_name="us-east-1")
        result = find_idle_lambda_functions(lmb, cw, dry_run=True)
        assert result == []

    def test_function_with_no_cloudwatch_data_flagged(self):
        from services.cost.idle_resources import find_idle_lambda_functions
        import zipfile, io as _io
        iam = boto3.client("iam", region_name="us-east-1")
        lmb = boto3.client("lambda", region_name="us-east-1")
        cw = boto3.client("cloudwatch", region_name="us-east-1")

        # Create IAM role that Lambda can assume (required by moto)
        assume_policy = json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }],
        })
        role = iam.create_role(
            RoleName="test-lambda-role",
            AssumeRolePolicyDocument=assume_policy,
        )
        role_arn = role["Role"]["Arn"]

        # Create a minimal zip for moto
        buf = _io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("lambda_function.py", "def handler(e, c): return {}")
        buf.seek(0)

        lmb.create_function(
            FunctionName="idle-fn",
            Runtime="python3.9",
            Role=role_arn,
            Handler="lambda_function.handler",
            Code={"ZipFile": buf.read()},
        )

        findings = find_idle_lambda_functions(lmb, cw, days=30)
        names = [f["function_name"] for f in findings]
        assert "idle-fn" in names


# ---------------------------------------------------------------------------
# idle_resources — NAT Gateways (moto)
# ---------------------------------------------------------------------------

@mock_aws
class TestFindIdleNatGateways:
    def test_dry_run_returns_empty(self):
        from services.cost.idle_resources import find_idle_nat_gateways
        ec2 = boto3.client("ec2", region_name="us-east-1")
        cw = boto3.client("cloudwatch", region_name="us-east-1")
        result = find_idle_nat_gateways(ec2, cw, dry_run=True)
        assert result == []


# ---------------------------------------------------------------------------
# idle_resources — find_all_idle_resources
# ---------------------------------------------------------------------------

class TestFindAllIdleResourcesDryRun:
    def test_all_sections_empty_in_dry_run(self):
        from services.cost.idle_resources import find_all_idle_resources
        ec2 = MagicMock()
        rds = MagicMock()
        lmb = MagicMock()
        elb = MagicMock()
        cw = MagicMock()
        findings = find_all_idle_resources(ec2, rds, lmb, elb, cw, dry_run=True)
        for key, val in findings.items():
            assert val == [], f"Expected empty list for {key} in dry-run mode"


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------

class TestFormatTable:
    def test_basic_table(self):
        from services.cost.report import format_table
        headers = ["Name", "Cost"]
        rows = [["EC2", "50.00"], ["RDS", "20.00"]]
        output = format_table(rows, headers)
        assert "Name" in output
        assert "EC2" in output
        assert "20.00" in output

    def test_separators_present(self):
        from services.cost.report import format_table
        output = format_table([["a", "b"]], ["H1", "H2"])
        assert "+" in output
        assert "|" in output


class TestFormatJson:
    def test_serialises_list(self):
        from services.cost.report import format_json
        data = [{"service": "EC2", "amount": 10.5}]
        out = format_json(data)
        parsed = json.loads(out)
        assert parsed[0]["service"] == "EC2"

    def test_serialises_datetime(self):
        from services.cost.report import format_json
        dt = datetime(2024, 1, 1, tzinfo=timezone.utc)
        out = format_json({"ts": dt})
        assert "2024" in out


class TestFormatCsv:
    def test_basic_csv(self):
        from services.cost.report import format_csv
        headers = ["Service", "Cost"]
        rows = [["EC2", "10.00"], ["S3", "2.00"]]
        out = format_csv(rows, headers)
        lines = out.strip().splitlines()
        assert lines[0] == "Service,Cost"
        assert "EC2" in lines[1]

    def test_header_row_present(self):
        from services.cost.report import format_csv
        out = format_csv([["a"]], ["H1"])
        assert out.startswith("H1")


class TestPrintReport:
    def test_json_output(self, capsys):
        from services.cost.report import print_report
        data = [{"service": "Lambda", "amount": 1.5}]
        print_report(data, output_format="json")
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed[0]["service"] == "Lambda"

    def test_table_output(self, capsys):
        from services.cost.report import print_report
        data = [{"Service": "EC2", "Amount": "5.00"}]
        print_report(data, output_format="table")
        captured = capsys.readouterr()
        assert "EC2" in captured.out

    def test_csv_output(self, capsys):
        from services.cost.report import print_report
        data = [{"Service": "S3", "Amount": "1.00"}]
        print_report(data, output_format="csv")
        captured = capsys.readouterr()
        assert "S3" in captured.out

    def test_empty_data_prints_no_results(self, capsys):
        from services.cost.report import print_report
        print_report([], headers=["A", "B"], output_format="table")
        captured = capsys.readouterr()
        assert "no results" in captured.out.lower()


class TestPrintIdleReport:
    def test_json_mode(self, capsys):
        from services.cost.report import print_idle_report
        findings = {
            "ec2": [], "ebs_volumes": [], "elastic_ips": [], "snapshots": [],
            "rds": [], "lambda": [], "load_balancers": [], "nat_gateways": [],
        }
        print_idle_report(findings, output_format="json")
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert "ec2" in parsed

    def test_table_mode_shows_total(self, capsys):
        from services.cost.report import print_idle_report
        findings = {
            "ec2": [
                {
                    "instance_id": "i-abc", "instance_type": "t3.medium",
                    "state": "stopped", "avg_cpu_pct": None,
                    "reason": "stopped", "estimated_monthly_waste_usd": 30.37,
                    "recommendation": "terminate",
                }
            ],
            "ebs_volumes": [], "elastic_ips": [], "snapshots": [],
            "rds": [], "lambda": [], "load_balancers": [], "nat_gateways": [],
        }
        print_idle_report(findings, output_format="table")
        captured = capsys.readouterr()
        assert "30.37" in captured.out
        assert "total" in captured.out.lower()


# ---------------------------------------------------------------------------
# cost_analyser CLI
# ---------------------------------------------------------------------------

class TestCostAnalyserCli:
    """Smoke-tests for the CLI argument parser (no network calls)."""

    def _run(self, argv):
        from cost_analyser import _build_parser
        parser = _build_parser()
        return parser.parse_args(argv)

    def test_breakdown_defaults(self):
        args = self._run(["breakdown"])
        assert args.command == "breakdown"
        assert args.granularity == "MONTHLY"
        assert args.top == 10
        assert args.dry_run is False

    def test_breakdown_custom_flags(self):
        args = self._run([
            "breakdown", "--since", "2024-01-01", "--until", "2024-01-31",
            "--granularity", "DAILY", "--tag", "team", "--top", "5", "--dry-run",
        ])
        assert args.since == "2024-01-01"
        assert args.granularity == "DAILY"
        assert args.top == 5
        assert args.dry_run is True

    def test_estimate_ec2(self):
        args = self._run(["estimate", "--resource-type", "ec2",
                           "--instance-type", "t3.medium"])
        assert args.resource_type == "ec2"
        assert args.instance_type == "t3.medium"

    def test_estimate_rds(self):
        args = self._run(["estimate", "--resource-type", "rds",
                           "--db-instance-class", "db.m5.large", "--multi-az"])
        assert args.multi_az is True

    def test_idle_defaults(self):
        args = self._run(["idle"])
        assert args.cpu_threshold == 5.0
        assert args.idle_days == 14
        assert args.snapshot_age_days == 90

    def test_idle_custom_thresholds(self):
        args = self._run(["idle", "--cpu-threshold", "10", "--idle-days", "30"])
        assert args.cpu_threshold == 10.0
        assert args.idle_days == 30

    def test_tags_command(self):
        args = self._run(["tags", "--tag", "environment"])
        assert args.command == "tags"
        assert args.tag == "environment"

    def test_budgets_command(self):
        args = self._run(["budgets"])
        assert args.command == "budgets"

    def test_output_choices(self):
        for fmt in ("table", "json", "csv"):
            args = self._run(["breakdown", "--output", fmt])
            assert args.output == fmt

    def test_missing_required_subcommand_raises(self):
        from cost_analyser import _build_parser
        parser = _build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])
