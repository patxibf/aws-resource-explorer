from typing import List
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate
import boto3

S3_STORAGE_PRICE_PER_GB = 0.023

def get_s3_storage_price(region: str = "us-east-1") -> float:
    try:
        pricing = boto3.client("pricing", region_name="us-east-1")
        response = pricing.get_products(
            ServiceCode="AmazonS3",
            Filters=[{"Type": "TERM_MATCH", "Field": "storageClass", "Value": "Standard"}],
            RegionCode=region,
        )
        for price in response.get("PriceList", []):
            usd = list(list(price["terms"]["onDemand"].values())[0]["priceDimensions"].values())[0]["pricePerUnit"]["USD"]
            return float(usd)
        return S3_STORAGE_PRICE_PER_GB
    except Exception:
        return S3_STORAGE_PRICE_PER_GB

@register
class S3Scanner(BaseScanner):
    SERVICE_NAME = "s3"

    def scan(self) -> List[Resource]:
        client = self.session.client(self.SERVICE_NAME, region_name=self.region)
        resources = []

        try:
            response = client.list_buckets()
            for bucket in response.get("Buckets", []):
                name = bucket["Name"]
                tags_response = client.get_bucket_tagging(Bucket=name)
                tags = {t["Key"]: t["Value"] for t in tags_response.get("TagSet", [])}
                cost = CostEstimate(0.50, "static")
                resources.append(Resource(name=name, resource_type="s3.bucket", region=self.region, status="active", cost=cost, tags=tags))
        except Exception:
            pass

        return resources