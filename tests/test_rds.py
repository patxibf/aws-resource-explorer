from scanners.rds import RDSScanner

def test_rds_scanner_stopped_instance():
    class MockPaginator:
        def __init__(self, func):
            self.func = func
        def paginate(self, MaxRecords=None):
            return [self.func()]

    class MockRDS:
        def get_paginator(self, operation_name):
            return MockPaginator(lambda: {
                "DBInstances": [{
                    "DBInstanceIdentifier": "prod-db",
                    "DBInstanceClass": "db.t3.medium",
                    "DBInstanceStatus": "stopped",
                    "Tags": [{"Key": "Env", "Value": "production"}]
                }]
            })

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
        def get_paginator(self, operation_name):
            return MockPaginator(lambda: {
                "DBInstances": [{
                    "DBInstanceIdentifier": "prod-db",
                    "DBInstanceClass": "db.t3.medium",
                    "DBInstanceStatus": "available",
                    "Tags": [{"Key": "Env", "Value": "production"}]
                }]
            })

    class MockSession:
        def client(self, service, region_name=None):
            return MockRDS()

    scanner = RDSScanner(MockSession(), "us-east-1")
    resources = scanner.scan()
    assert len(resources) == 1
    assert resources[0].name == "prod-db"
    assert resources[0].status == "available"
    assert resources[0].cost.monthly_usd > 0.0
