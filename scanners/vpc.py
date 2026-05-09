from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

@register
class VPCScanner(BaseScanner):
    SERVICE_NAME = "ec2"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []

        for vpc in client.describe_vpcs().get("Vpcs", []):
            resources.append(Resource(
                name=next((t["Value"] for t in vpc.get("Tags", []) if t["Key"] == "Name"), vpc["VpcId"]),
                resource_type="vpc",
                region=self.region,
                status="available",
                cost=CostEstimate(0.0, "static"),
                tags={t["Key"]: t["Value"] for t in vpc.get("Tags", [])}
            ))

        for subnet in client.describe_subnets().get("Subnets", []):
            resources.append(Resource(
                name=next((t["Value"] for t in subnet.get("Tags", []) if t["Key"] == "Name"), subnet["SubnetId"]),
                resource_type="vpc.subnet",
                region=self.region,
                status=subnet["State"],
                cost=CostEstimate(0.0, "static"),
                tags={t["Key"]: t["Value"] for t in subnet.get("Tags", [])}
            ))

        for igw in client.describe_internet_gateways().get("InternetGateways", []):
            resources.append(Resource(
                name=next((t["Value"] for t in igw.get("Tags", []) if t["Key"] == "Name"), igw["InternetGatewayId"]),
                resource_type="vpc.igw",
                region=self.region,
                status="available",
                cost=CostEstimate(0.0, "static"),
                tags={t["Key"]: t["Value"] for t in igw.get("Tags", [])}
            ))

        for endpoint in client.describe_vpc_endpoints().get("VpcEndpoints", []):
            resources.append(Resource(
                name=endpoint["VpcEndpointId"],
                resource_type=f"vpc.endpoint.{endpoint['ServiceType']}",
                region=self.region,
                status=endpoint["State"],
                cost=CostEstimate(0.0, "static"),
                tags={}
            ))

        return resources
