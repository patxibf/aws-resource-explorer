from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

@register
class APIGatewayScanner(BaseScanner):
    SERVICE_NAME = "apigateway"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        try:
            rest_apis = client.get_rest_apis().get("items", [])
            for api in rest_apis:
                resources.append(Resource(
                    name=api["name"],
                    resource_type="apigateway.rest",
                    region=self.region,
                    status="ACTIVE" if api["endpointConfiguration"]["types"][0] != "PRIVATE" else "PRIVATE",
                    cost=CostEstimate(3.50, "static"),
                    tags={}
                ))
        except Exception:
            pass
        return resources