from typing import List
import sys
import boto3
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

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
            price_per_gb = get_s3_storage_price(self.region)
            for bucket in response.get("Buckets", []):
                name = bucket["Name"]
                tags = {}
                try:
                    tags_response = client.get_bucket_tagging(Bucket=name)
                    tags = {t["Key"]: t["Value"] for t in tags_response.get("TagSet", [])}
                except Exception as e:
                    print(f"[s3] no tagset or error for bucket {name}: {type(e).__name__}", file=sys.stderr)

                size_bytes = 0
                try:
                    paginator = client.get_paginator("list_objects_v2")
                    for page in paginator.paginate(Bucket=name, PaginationConfig={"MaxKeys": 1000}):
                        for obj in page.get("Contents", []):
                            size_bytes += obj.get("Size", 0)
                except Exception:
                    pass

                size_gb = size_bytes / (1024**3)
                cost = CostEstimate(size_gb * price_per_gb, "static")
                resources.append(Resource(name=name, resource_type="s3.bucket", region=self.region, status="active", cost=cost, tags=tags))
        except Exception as e:
            print(f"[s3] scan failed: {type(e).__name__}", file=sys.stderr)

        return resources