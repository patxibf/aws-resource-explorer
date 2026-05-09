from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate
from costs import estimate_ec2_cost

@register
class EC2Scanner(BaseScanner):
    SERVICE_NAME = "ec2"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        paginator = client.get_paginator("describe_instances")

        for page in paginator.paginate(MaxResults=100):
            for reservation in page.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    resources.append(self._parse_instance(instance))

        return resources

    def _parse_instance(self, instance: dict) -> Resource:
        name = next((t["Value"] for t in instance.get("Tags", []) if t["Key"] == "Name"), instance["InstanceId"])
        state = instance["State"]["Name"]
        instance_type = instance["InstanceType"]
        cost = estimate_ec2_cost(instance_type, state)
        tags = {t["Key"]: t["Value"] for t in instance.get("Tags", [])}
        return Resource(name=name, resource_type="ec2.instance", region=self.region, status=state, cost=cost, tags=tags)
