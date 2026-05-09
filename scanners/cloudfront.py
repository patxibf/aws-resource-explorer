from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

@register
class CloudFrontScanner(BaseScanner):
    SERVICE_NAME = "cloudfront"

    def __init__(self, session, region: str, regions: List[str]):
        super().__init__(session, region)
        self.regions = regions

    def scan(self) -> List[Resource]:
        if self.region != self.regions[0]:
            return []
        client = self.session.client(self.SERVICE_NAME)
        resources = []
        try:
            response = client.list_distributions()
            for dist in response.get("Items", []):
                resources.append(Resource(
                    name=dist["DomainName"],
                    resource_type="cloudfront.distribution",
                    region="global",
                    status="Enabled" if dist["Enabled"] else "Disabled",
                    cost=CostEstimate(0.085, "static"),
                    tags={t["Key"]: t["Value"] for t in dist.get("Tags", {}).get("Items", [])}
                ))
        except Exception:
            pass
        return resources
