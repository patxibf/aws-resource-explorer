from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

@register
class SNSScanner(BaseScanner):
    SERVICE_NAME = "sns"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        try:
            topics = client.list_topics().get("Topics", [])
            for topic in topics:
                resources.append(Resource(
                    name=topic["TopicArn"].split(":")[-1],
                    resource_type="sns.topic",
                    region=self.region,
                    status="active",
                    cost=CostEstimate(0.5, "static"),  # per million
                    tags={}
                ))
        except Exception:
            pass
        return resources
