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
                endpoint_config = api.get("endpointConfiguration", {})
                    types = endpoint_config.get("types", [])
                    endpoint_type = types[0] if types else None
                    status = "ACTIVE" if endpoint_type != "PRIVATE" else "PRIVATE"
                    resources.append(Resource(
                    name=api["name"],
                    resource_type="apigateway.rest",
                    region=self.region,
                    status=status,
                    cost=CostEstimate(3.50, "static"),
                    tags={}
                ))
        except Exception:
            pass
        return resources