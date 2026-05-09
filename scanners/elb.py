from typing import List
import sys
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate
from costs import estimate_elb_cost

@register
class ELBScanner(BaseScanner):
    SERVICE_NAME = "elbv2"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []

        try:
            response = client.describe_load_balancers()
            for lb in response.get("LoadBalancers", []):
                resources.append(self._parse_lb(lb, client))
        except Exception:
            pass

        return resources

    def _parse_lb(self, lb: dict, client) -> Resource:
        name = lb["LoadBalancerName"]
        lb_type = lb["Type"]
        state = lb["State"]["Code"] if "State" in lb else "active"
        cost = estimate_elb_cost(lb_type, state)
        tags = {}
        try:
            arn = lb["LoadBalancerArn"]
            tags_response = client.describe_tags(ResourceArns=[arn])
            tags = {t["Key"]: t["Value"] for t in tags_response.get("TagDescriptions", [{}])[0].get("Tags", [])}
        except Exception:
            print(f"[elbv2] failed to get tags for {name}: {type(e).__name__}", file=sys.stderr)
        return Resource(name=name, resource_type=f"elb.{lb_type}", region=self.region, status=state, cost=cost, tags=tags)