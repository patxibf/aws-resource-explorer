from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate
from costs import estimate_lambda_cost

@register
class LambdaScanner(BaseScanner):
    SERVICE_NAME = "lambda"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        paginator = client.get_paginator("list_functions")

        for page in paginator.paginate(MaxItems=100):
            for func in page.get("Functions", []):
                resources.append(self._parse_function(func))
        return resources

    def _parse_function(self, func: dict) -> Resource:
        name = func["FunctionName"]
        state = func.get("State", "Active")
        memory_size_mb = func.get("MemorySize", 128)
        timeout = func.get("Timeout", 3)

        # Estimate Lambda cost: assume ~12 hours/month of execution (e.g., 1 invocation/hour)
        invocations_per_month = 12 * 30  # 12 hours/month
        gb_seconds = (memory_size_mb / 1024) * timeout * invocations_per_month
        cost = estimate_lambda_cost(invocations=invocations_per_month, gb_seconds=gb_seconds)

        arn = func["FunctionArn"]
        tags_response = client.list_tags(Resource=arn)
        tags = {t["Key"]: t["Value"] for t in tags_response.get("Tags", [])}
        return Resource(name=name, resource_type="lambda.function", region=self.region, status=state.lower(), cost=cost, tags=tags)