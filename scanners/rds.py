from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate
from costs import estimate_rds_cost

@register
class RDSScanner(BaseScanner):
    SERVICE_NAME = "rds"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        paginator = client.get_paginator("describe_db_instances")

        for page in paginator.paginate(MaxRecords=100):
            for db in page.get("DBInstances", []):
                resources.append(self._parse_db(db))

        return resources

    def _parse_db(self, db: dict) -> Resource:
        name = db["DBInstanceIdentifier"]
        status = db["DBInstanceStatus"]
        instance_class = db["DBInstanceClass"]
        cost = estimate_rds_cost(instance_class, status)
        arn = db["DBInstanceArn"]
        tags_response = client.list_tags_for_resource(ResourceName=arn)
        tags = {t["Key"]: t["Value"] for t in tags_response.get("TagList", [])}
        return Resource(name=name, resource_type="rds.instance", region=self.region, status=status, cost=cost, tags=tags)
