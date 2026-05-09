#!/usr/bin/env python3
import argparse
import boto3
import sys
import os
from datetime import datetime
from config import ensure_config, get_regions, interactive_setup
from models import Resource
from scanners import get_scanners

def print_header():
    print("=" * 60)
    print("AWS RESOURCE EXPLORER")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 60)

def print_summary(all_resources: list):
    total_cost = sum(r.cost.monthly_usd for r in all_resources)
    total_count = len(all_resources)

    status_counts = {}
    for r in all_resources:
        status_counts[r.status] = status_counts.get(r.status, 0) + 1

    by_service = {}
    for r in all_resources:
        by_service[r.resource_type] = by_service.get(r.resource_type, {"count": 0, "cost": 0.0})
        by_service[r.resource_type]["count"] += 1
        by_service[r.resource_type]["cost"] += r.cost.monthly_usd

    by_region = {}
    for r in all_resources:
        by_region[r.region] = by_region.get(r.region, {"count": 0, "cost": 0.0})
        by_region[r.region]["count"] += 1
        by_region[r.region]["cost"] += r.cost.monthly_usd

    print(f"\nTOTAL ESTIMATED MONTHLY COST: ${total_cost:.2f}")
    print(f"Total resources: {total_count}")
    print(f"\nSTATUS BREAKDOWN")
    print("-" * 40)
    for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
        print(f"  {status:20} {count:5}")

    print(f"\nBY SERVICE")
    print("-" * 60)
    print(f"{'Service':<25} {'Count':>8} {'Est. Monthly':>15}")
    for svc, data in sorted(by_service.items(), key=lambda x: -x[1]["cost"]):
        print(f"{svc:<25} {data['count']:>8} ${data['cost']:>14.2f}")

    print(f"\nBY REGION")
    print("-" * 60)
    print(f"{'Region':<20} {'Count':>8} {'Est. Monthly':>15}")
    for region, data in sorted(by_region.items(), key=lambda x: -x[1]["cost"]):
        print(f"{region:<20} {data['count']:>8} ${data['cost']:>14.2f}")

    print(f"\nALL RESOURCES")
    print("-" * 60)
    print(f"{'Name':<40} {'Type':<20} {'Region':<15} {'Status':<12} {'Est. Cost'}")
    for r in sorted(all_resources, key=lambda x: -x.cost.monthly_usd):
        cost_str = f"${r.cost.monthly_usd:.2f}" if r.cost.monthly_usd > 0 else "—"
        print(f"{r.name:<40} {r.resource_type:<20} {r.region:<15} {r.status:<12} {cost_str}")

def main():
    parser = argparse.ArgumentParser(description="AWS Resource Explorer")
    parser.add_argument("--configure", action="store_true", help="Run interactive setup")
    args = parser.parse_args()

    if args.configure:
        print("Running configuration setup...")
        regions = interactive_setup()
        config = {"regions": regions}
        from config import save_config
        save_config(config)
        print(f"Config saved. Run without --configure to start scanning.")
        sys.exit(0)

    config = ensure_config()
    regions = get_regions(config)

    if not regions:
        print("No regions configured. Run with --configure to set up.")
        sys.exit(1)

    print_header()
    print(f"\nScanning regions: {', '.join(regions)}")

    all_resources = []

    from concurrent.futures import ThreadPoolExecutor, as_completed

    def scan_region(region: str):
        session = boto3.Session()
        resources = []
        for scanner_class in get_scanners():
            try:
                if getattr(scanner_class, "IS_GLOBAL", False) and region != regions[0]:
                    continue
                scanner = scanner_class(session, region)
                resources.extend(scanner.scan())
            except Exception as e:
                print(f"Warning: {scanner_class.__name__} in {region}: {e}")
        return region, resources

    with ThreadPoolExecutor(max_workers=max(len(regions), 1)) as executor:
        futures = {executor.submit(scan_region, r): r for r in regions}
        for future in as_completed(futures):
            region, resources = future.result()
            print(f"  {region}: {len(resources)} resources")
            all_resources.extend(resources)

    print_summary(all_resources)

if __name__ == "__main__":
    main()