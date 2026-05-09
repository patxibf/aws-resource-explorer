from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

@register
class ECSScanner(BaseScanner):
    SERVICE_NAME = "ecs"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        try:
            clusters = client.list_clusters().get("clusterArns", [])
            for arn in clusters:
                cluster = client.describe_clusters(clusters=[arn])["clusters"][0]
                resources.append(Resource(
                    name=cluster["clusterName"],
                    resource_type="ecs.cluster",
                    region=self.region,
                    status=cluster["status"],
                    cost=CostEstimate(0.05, "static"),
                    tags={}
                ))
        except Exception:
            pass
        return resources