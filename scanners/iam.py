from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

@register
class IAMScanner(BaseScanner):
    IS_GLOBAL = True
    SERVICE_NAME = "iam"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME)
        resources = []

        try:
            for user in client.list_users().get("Users", []):
                resources.append(Resource(
                    name=user["UserName"],
                    resource_type="iam.user",
                    region="global",
                    status="active",
                    cost=CostEstimate(0.0, "static"),
                    tags={}
                ))
        except Exception:
            pass

        try:
            for role in client.list_roles().get("Roles", []):
                resources.append(Resource(
                    name=role["RoleName"],
                    resource_type="iam.role",
                    region="global",
                    status="active",
                    cost=CostEstimate(0.0, "static"),
                    tags={}
                ))
        except Exception:
            pass

        return resources
