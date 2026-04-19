class Scan:
    def __init__(self, scan_id=None, target_url="", total_findings=0, error_message=None, created_at=None):
        self.id = scan_id
        self.target_url = target_url
        self.total_findings = total_findings
        self.error_message = error_message
        self.created_at = created_at