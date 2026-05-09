from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

@register
class FSxScanner(BaseScanner):
    SERVICE_NAME = "fsx"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        try:
            filesystems = client.describe_file_systems().get("FileSystems", [])
            for fs in filesystems:
                resources.append(Resource(
                    name=fs["FileSystemId"],
                    resource_type="fsx.filesystem",
                    region=self.region,
                    status=fs["Lifecycle"],
                    cost=CostEstimate(0.075, "static"),  # per GB/month
                    tags={}
                ))
        except Exception:
            pass
        return resources
