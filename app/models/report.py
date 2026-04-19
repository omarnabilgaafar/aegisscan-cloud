class Report:
    def __init__(self, report_id=None, scan_id=None, path="", created_at=None):
        self.id = report_id
        self.scan_id = scan_id
        self.path = path
        self.created_at = created_at