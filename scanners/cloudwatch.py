from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

@register
class CloudWatchScanner(BaseScanner):
    SERVICE_NAME = "cloudwatch"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []
        try:
            dashboards = client.list_dashboards().get("DashboardEntries", [])
            for d in dashboards:
                resources.append(Resource(
                    name=d["DashboardName"],
                    resource_type="cloudwatch.dashboard",
                    region=self.region,
                    status="active",
                    cost=CostEstimate(0.0, "static"),
                    tags={}
                ))
        except Exception:
            pass
        try:
            alarms = client.describe_alarms().get("MetricAlarms", [])
            for alarm in alarms:
                resources.append(Resource(
                    name=alarm["AlarmName"],
                    resource_type="cloudwatch.alarm",
                    region=self.region,
                    status="active" if alarm["StateValue"] == "OK" else alarm["StateValue"].lower(),
                    cost=CostEstimate(0.0, "static"),
                    tags={}
                ))
        except Exception:
            pass
        return resources
