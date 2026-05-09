from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

@register
class SQSScanner(BaseScanner):
    SERVICE_NAME = "sqs"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        try:
            queues = client.list_queues().get("QueueUrls", [])
            for url in queues:
                queue = client.get_queue_attributes(QueueUrl=url, AttributeNames=["QueueName"])["Attributes"]
                resources.append(Resource(
                    name=queue["QueueName"],
                    resource_type="sqs.queue",
                    region=self.region,
                    status="active",
                    cost=CostEstimate(0.0, "static"),
                    tags={}
                ))
        except Exception:
            pass
        return resources
