from scanners.rds import RDSScanner

def test_rds_scanner_stopped_instance():
    class MockPaginator:
        def __init__(self, func):
            self.func = func
        def paginate(self, MaxRecords=None):
            return [self.func()]

    class MockRDS:
        def __init__(self):
            self.instances = [{
                "DBInstanceIdentifier": "prod-db",
                "DBInstanceClass": "db.t3.medium",
                "DBInstanceStatus": "stopped",
                "DBInstanceArn": "arn:aws:rds:us-east-1:123456789012:db:prod-db"
            }]
        def get_paginator(self, operation_name):
            return MockPaginator(lambda: {"DBInstances": self.instances})
        def list_tags_for_resource(self, ResourceName):
            return {"TagList": [{"Key": "Env", "Value": "production"}]}

    class MockSession:
        def client(self, service, region_name=None):
            return MockRDS()

    scanner = RDSScanner(MockSession(), "us-east-1")
    resources = scanner.scan()
    assert len(resources) == 1
    assert resources[0].name == "prod-db"
    assert resources[0].status == "stopped"
    assert resources[0].cost.monthly_usd == 0.0

def test_rds_scanner_running_instance():
    class MockPaginator:
        def __init__(self, func):
            self.func = func
        def paginate(self, MaxRecords=None):
            return [self.func()]

    class MockRDS:
        def __init__(self):
            self.instances = [{
                "DBInstanceIdentifier": "prod-db",
                "DBInstanceClass": "db.t3.medium",
                "DBInstanceStatus": "available",
                "DBInstanceArn": "arn:aws:rds:us-east-1:123456789012:db:prod-db"
            }]
        def get_paginator(self, operation_name):
            return MockPaginator(lambda: {"DBInstances": self.instances})
        def list_tags_for_resource(self, ResourceName):
            return {"TagList": [{"Key": "Env", "Value": "production"}]}

    class MockSession:
        def client(self, service, region_name=None):
            return MockRDS()

    scanner = RDSScanner(MockSession(), "us-east-1")
    resources = scanner.scan()
    assert len(resources) == 1
    assert resources[0].name == "prod-db"
    assert resources[0].status == "available"
    assert resources[0].cost.monthly_usd > 0.0