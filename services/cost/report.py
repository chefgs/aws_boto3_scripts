"""Output formatting helpers — table, JSON, and CSV."""
import csv
import io
import json
import logging

logger = logging.getLogger(__name__)

_COLUMN_PAD = 2


def _col_widths(headers, rows):
    """Return a list of column widths based on headers and row data."""
    widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    return widths


def format_table(rows, headers):
    """Render *rows* as a plain-text ASCII table with the given *headers*.

    Parameters
    ----------
    rows    : list of iterables (one per data row)
    headers : list of column header strings

    Returns
    -------
    str
    """
    rows = [list(r) for r in rows]
    widths = _col_widths(headers, rows)
    pad = _COLUMN_PAD

    sep = "+" + "+".join("-" * (w + pad * 2) for w in widths) + "+"
    header_line = "|" + "|".join(
        f" {str(h).ljust(w + pad)} " for h, w in zip(headers, widths)
    ) + "|"

    lines = [sep, header_line, sep]
    for row in rows:
        line = "|" + "|".join(
            f" {str(c).ljust(w + pad)} " for c, w in zip(row, widths)
        ) + "|"
        lines.append(line)
    lines.append(sep)
    return "\n".join(lines)


def format_json(data):
    """Serialise *data* to an indented JSON string.

    Parameters
    ----------
    data : any JSON-serialisable object

    Returns
    -------
    str
    """
    return json.dumps(data, indent=2, default=str)


def format_csv(rows, headers):
    """Render *rows* as a CSV string with a header row.

    Parameters
    ----------
    rows    : list of iterables
    headers : list of column header strings

    Returns
    -------
    str
    """
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return buf.getvalue()


def print_report(data, headers=None, output_format="table"):
    """Print *data* to stdout in the requested format.

    Parameters
    ----------
    data          : list of dicts or list of lists
    headers       : column headers (required for 'table' and 'csv' when data is a list of dicts)
    output_format : 'table' | 'json' | 'csv'
    """
    output_format = (output_format or "table").lower()

    if output_format == "json":
        print(format_json(data))
        return

    # Normalise to list-of-lists for table / csv
    if data and isinstance(data[0], dict):
        if headers is None:
            headers = list(data[0].keys())
        rows = [[row.get(h, "") for h in headers] for row in data]
    else:
        rows = [list(r) for r in (data or [])]
        if headers is None:
            headers = []

    if output_format == "csv":
        print(format_csv(rows, headers))
    else:
        if not rows:
            print("(no results)")
            return
        print(format_table(rows, headers))


def print_idle_report(findings, output_format="table"):
    """Pretty-print idle-resource findings grouped by resource type.

    Parameters
    ----------
    findings      : dict returned by ``find_all_idle_resources``
    output_format : 'table' | 'json' | 'csv'
    """
    if output_format == "json":
        print(format_json(findings))
        return

    section_headers = {
        "ec2": ["Instance ID", "Type", "State", "Avg CPU %", "Waste $/mo", "Reason"],
        "ebs_volumes": ["Volume ID", "Type", "Size GB", "State", "Waste $/mo", "Recommendation"],
        "elastic_ips": ["Allocation ID", "Public IP", "Waste $/mo", "Recommendation"],
        "snapshots": ["Snapshot ID", "Size GB", "Start Time", "Age Days", "Recommendation"],
        "rds": ["DB ID", "Class", "Engine", "State", "Multi-AZ", "Avg CPU %", "Waste $/mo", "Reason"],
        "lambda": ["Function Name", "Runtime", "Last Modified", "Reason", "Recommendation"],
        "load_balancers": ["ARN (short)", "Name", "Type", "State", "Reason", "Recommendation"],
        "nat_gateways": ["NAT GW ID", "VPC ID", "State", "Bytes Out", "Waste $/mo", "Reason"],
    }

    row_extractors = {
        "ec2": lambda f: [
            f["instance_id"], f["instance_type"], f["state"],
            f.get("avg_cpu_pct", "N/A"),
            f"${f['estimated_monthly_waste_usd']:.2f}",
            f["reason"],
        ],
        "ebs_volumes": lambda f: [
            f["volume_id"], f["volume_type"], f["size_gb"], f["state"],
            f"${f['estimated_monthly_waste_usd']:.2f}",
            f["recommendation"],
        ],
        "elastic_ips": lambda f: [
            f["allocation_id"], f["public_ip"],
            f"${f['estimated_monthly_waste_usd']:.2f}",
            f["recommendation"],
        ],
        "snapshots": lambda f: [
            f["snapshot_id"], f["volume_size_gb"], f["start_time"], f["age_days"],
            f["recommendation"],
        ],
        "rds": lambda f: [
            f["db_instance_id"], f["db_instance_class"], f["engine"], f["state"],
            f["multi_az"], f.get("avg_cpu_pct", "N/A"),
            f"${f['estimated_monthly_waste_usd']:.2f}",
            f["reason"],
        ],
        "lambda": lambda f: [
            f["function_name"], f["runtime"], f["last_modified"],
            f["reason"], f["recommendation"],
        ],
        "load_balancers": lambda f: [
            f["load_balancer_arn"][-30:], f["name"], f["type"], f["state"],
            f["reason"], f["recommendation"],
        ],
        "nat_gateways": lambda f: [
            f["nat_gateway_id"], f["vpc_id"], f["state"],
            f.get("bytes_out_total", "N/A"),
            f"${f['estimated_monthly_waste_usd']:.2f}",
            f["reason"],
        ],
    }

    total_waste = 0.0
    for section, items in findings.items():
        print(f"\n=== {section.upper().replace('_', ' ')} ===")
        if not items:
            print("  (none found)")
            continue
        rows = [row_extractors[section](item) for item in items]
        if output_format == "csv":
            print(format_csv(rows, section_headers[section]))
        else:
            print(format_table(rows, section_headers[section]))
        for item in items:
            total_waste += item.get("estimated_monthly_waste_usd", 0.0)

    print(f"\nEstimated total monthly waste: ${total_waste:.2f}")
