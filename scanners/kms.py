from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

@register
class KMSScanner(BaseScanner):
    SERVICE_NAME = "kms"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        try:
            keys = client.list_keys().get("Keys", [])
            for key in keys:
                info = client.describe_key(KeyId=key["KeyId"])["KeyMetadata"]
                resources.append(Resource(
                    name=info["KeyId"],
                    resource_type="kms.key",
                    region=self.region,
                    status=info["KeyState"],
                    cost=CostEstimate(1.0, "static"),
                    tags={}
                ))
        except Exception:
            pass
        return resources
