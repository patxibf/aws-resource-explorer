from models import CostEstimate

STATIC_COSTS = {
    "ec2.instance": {
        "type": "per_hour",
        "linux_on_demand": 0.0116,
        "sizes": {
            "t3.micro": 0.0104,
            "t3.small": 0.0208,
            "t3.medium": 0.0416,
            "t3.large": 0.0832,
            "t3.xlarge": 0.1664,
            "m5.large": 0.096,
            "m5.xlarge": 0.192,
        }
    },
    "rds.instance": {
        "type": "per_hour",
        "db.t3.micro": 0.017,
        "db.t3.small": 0.034,
        "db.t3.medium": 0.068,
    },
    "lambda": {
        "type": "per_request",
        "price_per_1m_requests": 0.20,
        "price_per_gb_second": 0.0000166667,
    },
    "natgateway": {
        "type": "per_hour",
        "price": 0.045,
    },
    "elb": {
        "type": "per_hour",
        "application": 0.0225,
        "network": 0.0225,
    },
}

def estimate_ec2_cost(instance_type: str, state: str) -> CostEstimate:
    if state in ("stopped", "terminated"):
        return CostEstimate(0.0, "static")
    price = STATIC_COSTS["ec2.instance"]["sizes"].get(instance_type, 0.064)
    return CostEstimate(price * 730, "static")  # ~730 hours/month

def estimate_rds_cost(instance_class: str, state: str) -> CostEstimate:
    if state in ("stopped", "deleted"):
        return CostEstimate(0.0, "static")
    price = STATIC_COSTS["rds.instance"].get(f"db.{instance_class}", 0.068)
    return CostEstimate(price * 730, "static")

def estimate_lambda_cost(invocations: int, gb_seconds: float) -> CostEstimate:
    monthly_requests_cost = (invocations / 1_000_000) * STATIC_COSTS["lambda"]["price_per_1m_requests"]
    monthly_compute_cost = (gb_seconds / 1_000_000) * STATIC_COSTS["lambda"]["price_per_gb_second"]
    return CostEstimate(monthly_requests_cost + monthly_compute_cost, "static")

def estimate_nat_cost(state: str) -> CostEstimate:
    if state == "available":
        return CostEstimate(STATIC_COSTS["natgateway"]["price"] * 730, "static")
    return CostEstimate(0.0, "static")

def estimate_elb_cost(lb_type: str, state: str) -> CostEstimate:
    if state != "active":
        return CostEstimate(0.0, "static")
    return CostEstimate(STATIC_COSTS["elb"]["application"] * 730, "static")