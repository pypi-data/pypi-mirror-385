#!/usr/bin/env python3
"""Analyze ModelAudit version scan results for sentence-transformers/all-MiniLM-L6-v2"""

import json
from pathlib import Path
from collections import defaultdict

RESULTS_DIR = Path("version_scan_results")
VERSIONS = ["0.1.5", "0.2.0", "0.2.1", "0.2.2", "0.2.3", "0.2.4", "0.2.5", "0.2.6", "0.2.7", "0.2.8"]

def load_result(version):
    """Load scan result for a specific version"""
    json_path = RESULTS_DIR / f"scan_{version}.json"
    if not json_path.exists():
        return None

    try:
        with open(json_path) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {version}: {e}")
        return None

def extract_key_metrics(result):
    """Extract key metrics from a scan result"""
    if not result:
        return None

    metrics = {
        "total_files": len(result.get("scanned_files", [])),
        "issues_count": len(result.get("issues", [])),
        "has_errors": result.get("has_errors", False),
        "exit_code": result.get("exit_code", 0),
        "scanners_used": set(),
        "issue_severities": defaultdict(int),
        "issue_types": defaultdict(int),
    }

    # Count issues by severity
    for issue in result.get("issues", []):
        severity = issue.get("severity", "unknown")
        metrics["issue_severities"][severity] += 1

        # Extract scanner from file path or message
        message = issue.get("message", "")
        metrics["issue_types"][message[:80]] += 1  # First 80 chars as type

    # Extract scanners used from scanned_files
    for file_info in result.get("scanned_files", []):
        if "scanner" in file_info:
            metrics["scanners_used"].add(file_info["scanner"])

    return metrics

def format_comparison():
    """Generate formatted comparison report"""
    print("=" * 100)
    print("ModelAudit Version Comparison: sentence-transformers/all-MiniLM-L6-v2")
    print("=" * 100)
    print()

    # Load all results
    results = {}
    for version in VERSIONS:
        results[version] = load_result(version)

    # Print summary table
    print("SUMMARY TABLE")
    print("-" * 100)
    print(f"{'Version':<10} {'Files':<8} {'Issues':<8} {'Critical':<10} {'Warning':<10} {'Info':<10} {'Exit Code':<10}")
    print("-" * 100)

    for version in VERSIONS:
        result = results[version]
        if not result:
            print(f"{version:<10} {'N/A':<8} {'N/A':<8} {'N/A':<10} {'N/A':<10} {'N/A':<10} {'FAILED':<10}")
            continue

        metrics = extract_key_metrics(result)
        if not metrics:
            print(f"{version:<10} {'ERROR':<8} {'ERROR':<8} {'ERROR':<10} {'ERROR':<10} {'ERROR':<10} {'ERROR':<10}")
            continue

        critical = metrics["issue_severities"].get("critical", 0)
        warning = metrics["issue_severities"].get("warning", 0)
        info = metrics["issue_severities"].get("info", 0)

        print(f"{version:<10} {metrics['total_files']:<8} {metrics['issues_count']:<8} "
              f"{critical:<10} {warning:<10} {info:<10} {metrics['exit_code']:<10}")

    print()
    print("=" * 100)
    print("KEY CHANGES BETWEEN VERSIONS")
    print("=" * 100)
    print()

    # Compare consecutive versions
    for i in range(len(VERSIONS) - 1):
        curr_ver = VERSIONS[i]
        next_ver = VERSIONS[i + 1]

        curr = results[curr_ver]
        next_result = results[next_ver]

        if not curr or not next_result:
            continue

        curr_metrics = extract_key_metrics(curr)
        next_metrics = extract_key_metrics(next_result)

        if not curr_metrics or not next_metrics:
            continue

        # Check for significant changes
        file_diff = next_metrics["total_files"] - curr_metrics["total_files"]
        issue_diff = next_metrics["issues_count"] - curr_metrics["issues_count"]

        if file_diff != 0 or issue_diff != 0:
            print(f"{curr_ver} → {next_ver}:")
            if file_diff != 0:
                print(f"  • Files scanned: {curr_metrics['total_files']} → {next_metrics['total_files']} ({file_diff:+d})")
            if issue_diff != 0:
                print(f"  • Issues detected: {curr_metrics['issues_count']} → {next_metrics['issues_count']} ({issue_diff:+d})")

            # Show severity changes
            for severity in ["critical", "warning", "info"]:
                curr_count = curr_metrics["issue_severities"].get(severity, 0)
                next_count = next_metrics["issue_severities"].get(severity, 0)
                if curr_count != next_count:
                    print(f"  • {severity.capitalize()} issues: {curr_count} → {next_count} ({next_count - curr_count:+d})")
            print()

    # Print detailed issue breakdown for first and last version
    print("=" * 100)
    print("DETAILED COMPARISON: First Working Version vs Latest")
    print("=" * 100)
    print()

    first_working = None
    for version in VERSIONS:
        if results[version]:
            first_working = version
            break

    if first_working and results[VERSIONS[-1]]:
        print(f"First Working: {first_working}")
        first_metrics = extract_key_metrics(results[first_working])
        for issue_type, count in sorted(first_metrics["issue_types"].items(), key=lambda x: -x[1])[:10]:
            print(f"  • {issue_type}: {count}")

        print()
        print(f"Latest: {VERSIONS[-1]}")
        latest_metrics = extract_key_metrics(results[VERSIONS[-1]])
        for issue_type, count in sorted(latest_metrics["issue_types"].items(), key=lambda x: -x[1])[:10]:
            print(f"  • {issue_type}: {count}")

if __name__ == "__main__":
    format_comparison()
