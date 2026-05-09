from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

@register
class LambdaScanner(BaseScanner):
    SERVICE_NAME = "lambda"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        paginator = client.get_paginator("list_functions")

        for page in paginator.paginate(MaxItems=100):
            for func in page.get("Functions", []):
                resources.append(self._parse_function(func, client))
        return resources

    def _parse_function(self, func: dict, client) -> Resource:
        name = func["FunctionName"]
        state = func.get("State", "Active")
        memory_size_mb = func.get("MemorySize", 128)
        timeout = func.get("Timeout", 3)

        # Cost estimation unavailable without CloudWatch data
        cost = CostEstimate(0.0, "unavailable")

        arn = func["FunctionArn"]
        tags_response = client.list_tags(Resource=arn)
        tags = {t["Key"]: t["Value"] for t in tags_response.get("Tags", [])}
        return Resource(name=name, resource_type="lambda.function", region=self.region, status=state.lower(), cost=cost, tags=tags)