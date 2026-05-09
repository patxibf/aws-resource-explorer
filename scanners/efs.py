from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

EFS_PRICE_PER_GB_MONTH = 0.30

@register
class EFSScanner(BaseScanner):
    SERVICE_NAME = "efs"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        try:
            filesystems = client.describe_file_systems().get("FileSystems", [])
            for fs in filesystems:
                size_bytes = fs.get("SizeInBytes", {}).get("Value", 0)
                size_gb = size_bytes / (1000**3)
                cost = CostEstimate(size_gb * EFS_PRICE_PER_GB_MONTH, "static")
                resources.append(Resource(
                    name=fs["FileSystemId"],
                    resource_type="efs.filesystem",
                    region=self.region,
                    status=fs["LifeCycleState"],
                    cost=cost,
                    tags={}
                ))
        except Exception:
            pass
        return resources
