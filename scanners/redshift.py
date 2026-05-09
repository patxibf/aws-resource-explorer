from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

@register
class RedshiftScanner(BaseScanner):
    SERVICE_NAME = "redshift"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        try:
            clusters = client.describe_clusters().get("Clusters", [])
            for cluster in clusters:
                status = cluster["ClusterStatus"]
                cost = CostEstimate(0.0, "static") if status == "deleted" else CostEstimate(0.25, "static")
                resources.append(Resource(
                    name=cluster["ClusterIdentifier"],
                    resource_type="redshift.cluster",
                    region=self.region,
                    status=status,
                    cost=cost,
                    tags={}
                ))
        except Exception:
            pass
        return resources
