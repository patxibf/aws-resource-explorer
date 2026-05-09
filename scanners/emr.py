from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

@register
class EMRScanner(BaseScanner):
    SERVICE_NAME = "emr"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        try:
            clusters = client.list_clusters().get("Clusters", [])
            for cluster in clusters:
                status = cluster["Status"]["State"]
                cost = CostEstimate(0.0, "static") if status == "TERMINATED" else CostEstimate(0.20, "static")
                resources.append(Resource(
                    name=cluster["Id"],
                    resource_type="emr.cluster",
                    region=self.region,
                    status=status,
                    cost=cost,
                    tags={}
                ))
        except Exception:
            pass
        return resources
