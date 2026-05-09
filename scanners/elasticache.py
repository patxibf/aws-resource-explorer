from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

@register
class ElastiCacheScanner(BaseScanner):
    SERVICE_NAME = "elasticache"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        try:
            clusters = client.describe_cache_clusters().get("CacheClusters", [])
            for cluster in clusters:
                status = cluster["CacheClusterStatus"]
                cost = CostEstimate(0.0, "static") if status == "deleted" or status == "failed" else CostEstimate(0.10, "static")
                resources.append(Resource(
                    name=cluster["CacheClusterId"],
                    resource_type="elasticache.cluster",
                    region=self.region,
                    status=status,
                    cost=cost,
                    tags={}
                ))
        except Exception:
            pass
        return resources
