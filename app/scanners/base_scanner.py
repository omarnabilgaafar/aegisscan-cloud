class BaseScanner:
    name = "Base Scanner"

    def scan(self, target, crawled_data=None):
        raise NotImplementedError("Subclasses must implement scan()")