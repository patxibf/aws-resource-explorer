import pytest
from scanners.ec2 import EC2Scanner

def test_ec2_scanner_returns_resources():
    class MockPaginator:
        def __init__(self, func):
            self.func = func
        def paginate(self, Filters=None, MaxResults=None):
            return [self.func()]

    class MockEC2:
        def __init__(self):
            self.instances_called = False
        def describe_instances(self, Filters=None, MaxResults=100):
            return {
                "Reservations": [{
                    "Instances": [{
                        "InstanceId": "i-12345",
                        "InstanceType": "t3.micro",
                        "State": {"Name": "running"},
                        "Tags": [{"Key": "Name", "Value": "test-server"}]
                    }]
                }]
            }
        def get_paginator(self, operation_name):
            self.instances_called = True
            return MockPaginator(lambda: {
                "Reservations": [{
                    "Instances": [{
                        "InstanceId": "i-12345",
                        "InstanceType": "t3.micro",
                        "State": {"Name": "running"},
                        "Tags": [{"Key": "Name", "Value": "test-server"}]
                    }]
                }]
            })

    class MockSession:
        def client(self, service, region_name=None):
            return MockEC2()

    scanner = EC2Scanner(MockSession(), "us-east-1")
    resources = scanner.scan()
    assert len(resources) == 1
    assert resources[0].name == "test-server"
    assert resources[0].resource_type == "ec2.instance"
    assert resources[0].status == "running"

def test_ec2_scanner_stopped_instance():
    class MockPaginator:
        def __init__(self, func):
            self.func = func
        def paginate(self, Filters=None, MaxResults=None):
            return [self.func()]

    class MockEC2:
        def get_paginator(self, operation_name):
            return MockPaginator(lambda: {
                "Reservations": [{
                    "Instances": [{
                        "InstanceId": "i-67890",
                        "InstanceType": "t3.medium",
                        "State": {"Name": "stopped"},
                        "Tags": [{"Key": "Name", "Value": "stopped-server"}]
                    }]
                }]
            })

    class MockSession:
        def client(self, service, region_name=None):
            return MockEC2()

    scanner = EC2Scanner(MockSession(), "us-east-1")
    resources = scanner.scan()
    assert len(resources) == 1
    assert resources[0].name == "stopped-server"
    assert resources[0].status == "stopped"
    assert resources[0].cost.monthly_usd == 0.0