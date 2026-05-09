from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

@register
class StorageGatewayScanner(BaseScanner):
    SERVICE_NAME = "storagegateway"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        try:
            gateways = client.list_gateways().get("Gateways", [])
            for gw in gateways:
                resources.append(Resource(
                    name=gw["GatewayName"],
                    resource_type="storagegateway.gateway",
                    region=self.region,
                    status=gw["GatewayOperationalState"],
                    cost=CostEstimate(0.0, "static"),
                    tags={}
                ))
        except Exception:
            pass
        return resources
