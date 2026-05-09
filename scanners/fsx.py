from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

FSX_PRICE_PER_GB_MONTH = 0.075

@register
class FSxScanner(BaseScanner):
    SERVICE_NAME = "fsx"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        try:
            filesystems = client.describe_file_systems().get("FileSystems", [])
            for fs in filesystems:
                storage_gib = fs.get("StorageCapacity", 0)
                size_gb = storage_gib * (1024**3) / (1000**3)
                cost = CostEstimate(size_gb * FSX_PRICE_PER_GB_MONTH, "static")
                resources.append(Resource(
                    name=fs["FileSystemId"],
                    resource_type="fsx.filesystem",
                    region=self.region,
                    status=fs["Lifecycle"],
                    cost=cost,
                    tags={}
                ))
        except Exception:
            pass
        return resources
