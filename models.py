from dataclasses import dataclass
from typing import Optional

@dataclass
class CostEstimate:
    monthly_usd: float
    estimate_type: str  # "static", "pricing_api", "unavailable"

@dataclass
class Resource:
    name: str
    resource_type: str  # e.g., "ec2.instance"
    region: str
    status: str  # e.g., "running", "stopped", "disabled"
    cost: CostEstimate
    tags: dict