from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

@register
class EKSScanner(BaseScanner):
    SERVICE_NAME = "eks"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        try:
            clusters = client.list_clusters().get("clusters", [])
            for name in clusters:
                cluster = client.describe_cluster(name=name)["cluster"]
                resources.append(Resource(
                    name=cluster["name"],
                    resource_type="eks.cluster",
                    region=self.region,
                    status=cluster["status"],
                    cost=CostEstimate(0.10, "static"),
                    tags={}
                ))
        except Exception:
            pass
        return resources