from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

@register
class Route53Scanner(BaseScanner):
    IS_GLOBAL = True
    SERVICE_NAME = "route53"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME)
        resources = []
        try:
            zones = client.list_hosted_zones().get("HostedZones", [])
            for zone in zones:
                resources.append(Resource(
                    name=zone["Name"].rstrip("."),
                    resource_type="route53.hostedzone",
                    region="global",
                    status="active",
                    cost=CostEstimate(0.5, "static"),  # per hosted zone/month
                    tags={}
                ))
        except Exception:
            pass
        return resources
