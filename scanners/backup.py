from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

@register
class BackupScanner(BaseScanner):
    SERVICE_NAME = "backup"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        try:
            vaults = client.list_backup_vaults().get("BackupVaultList", [])
            for vault in vaults:
                resources.append(Resource(
                    name=vault["BackupVaultName"],
                    resource_type="backup.vault",
                    region=self.region,
                    status="active",
                    cost=CostEstimate(0.0, "static"),
                    tags={}
                ))
        except Exception:
            pass
        return resources
