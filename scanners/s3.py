from typing import List
import sys
from functools import lru_cache
import boto3
from scanners.base import BaseScanner
from scanners import register
from models import Resource, CostEstimate

@lru_cache(maxsize=1)
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
        return 0.023
    except Exception:
        return 0.023

def get_bucket_size_bytes(client, bucket: str) -> int:
    try:
        cw = boto3.client("cloudwatch", region_name="us-east-1")
        result = cw.get_metric_statistics(
            Namespace="AWS/S3",
            MetricName="BucketSizeBytes",
            Period=86400,
            StartTime="2026-05-01T00:00:00Z",
            EndTime="2026-05-09T00:00:00Z",
            Statistics=["Average"],
            Dimensions=[{"Name": "BucketName", "Value": bucket}, {"Name": "StorageType", "Value": "StandardStorage"}]
        )
        if result.get("Datapoints"):
            return int(result["Datapoints"][0]["Average"])
    except Exception:
        pass
    return 0

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

                size_bytes = get_bucket_size_bytes(client, name)
                size_gb = size_bytes / (1024**3)
                cost = CostEstimate(size_gb * price_per_gb, "static")
                resources.append(Resource(name=name, resource_type="s3.bucket", region=self.region, status="active", cost=cost, tags=tags))
        except Exception as e:
            print(f"[s3] scan failed: {type(e).__name__}", file=sys.stderr)

        return resources