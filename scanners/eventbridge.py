from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

@register
class EventBridgeScanner(BaseScanner):
    SERVICE_NAME = "events"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        try:
            buses = client.list_event_buses().get("EventBuses", [])
            for bus in buses:
                resources.append(Resource(
                    name=bus["Name"],
                    resource_type="eventbridge.bus",
                    region=self.region,
                    status="active",
                    cost=CostEstimate(0.0, "static"),
                    tags={}
                ))
        except Exception:
            pass
        return resources
