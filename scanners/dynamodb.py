from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

@register
class DynamoDBScanner(BaseScanner):
    SERVICE_NAME = "dynamodb"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        try:
            tables = client.list_tables().get("TableNames", [])
            for name in tables:
                table = client.describe_table(TableName=name)["Table"]
                status = table["TableStatus"]
                cost = CostEstimate(0.25, "static")  # per GB/month
                resources.append(Resource(
                    name=name,
                    resource_type="dynamodb.table",
                    region=self.region,
                    status=status,
                    cost=cost,
                    tags={}
                ))
        except Exception:
            pass
        return resources
