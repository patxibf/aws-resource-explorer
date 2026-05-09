# AWS Resource Explorer

On-demand AWS resource scanner for cost optimization and operational monitoring.

Scans your AWS account across multiple regions and service types, aggregating resource counts, status breakdowns, and estimated monthly costs into a single sortable report.

## Features

- **Multi-region scanning** — Scan one or many AWS regions in parallel
- **30+ AWS services** — EC2, RDS, S3, Lambda, ECS, EKS, ElastiCache, ELB, CloudFront, DynamoDB, and more
- **Cost estimation** — Per-resource and aggregated monthly cost estimates
- **Status breakdown** — Running vs stopped vs disabled resources
- **Sorted output** — Full resource list sorted by cost (highest first)
- **Configurable** — Interactive setup and `--configure` flag for easy region management

## Setup

```bash
pip install -r requirements.txt
python explorer.py
```

On first run, you'll be prompted to enter the AWS regions to scan. This is saved to `~/.aws-explorer-config.json`.

## Usage

```bash
python explorer.py                  # Run scan
python explorer.py --configure     # Reconfigure regions
```

## Output

- Total estimated monthly cost
- Resource count by service
- Per-region summary
- Status breakdown (running/stopped/disabled)
- Full resource list sorted by cost

## Architecture

```
explorer.py          # Entry point, orchestrates scanning and reporting
config.py            # Region config persistence (~/.aws-explorer-config.json)
models.py            # Resource and cost data models
costs.py             # Cost estimation logic per service
scanners/
  base.py            # Base scanner interface
  ec2.py, rds.py, s3.py, ...  # Service-specific scanners
```

Scanners run in parallel via `ThreadPoolExecutor`, one thread per region. Each scanner queries boto3 and returns a list of `Resource` objects with name, type, region, status, and cost.

## Requirements

- Python 3.8+
- AWS credentials configured (e.g., `aws configure` or environment variables / IAM role)