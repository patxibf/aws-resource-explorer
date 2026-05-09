from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate
from costs import estimate_nat_cost

@register
class NATScanner(BaseScanner):
    SERVICE_NAME = "ec2"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        response = client.describe_nat_gateways()
        for nat in response.get("NatGateways", []):
            resources.append(self._parse_nat(nat))
        return resources

    def _parse_nat(self, nat: dict) -> Resource:
        name = next((t["Value"] for t in nat.get("Tags", []) if t["Key"] == "Name"), nat["NatGatewayId"])
        state = nat["State"]
        cost = estimate_nat_cost(state)
        tags = {t["Key"]: t["Value"] for t in nat.get("Tags", [])}
        return Resource(name=name, resource_type="nat.gateway", region=self.region, status=state, cost=cost, tags=tags)