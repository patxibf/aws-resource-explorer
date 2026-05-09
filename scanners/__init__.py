from scanners.base import BaseScanner

SCANNERS = []

def register(scanner_class):
    SCANNERS.append(scanner_class)
    return scanner_class

def get_scanners():
    return list(SCANNERS)

# Auto-import all scanners to trigger @register decorators
from scanners import (
    ec2, rds, s3, lambda_func, ecs, eks, elb, apigateway, nat,
    vpc, cloudfront, elasticache, redshift, emr, dynamodb,
    cloudwatch, sqs, sns, eventbridge, kms, iam, route53,
    efs, fsx, backup, storage_gateway
)