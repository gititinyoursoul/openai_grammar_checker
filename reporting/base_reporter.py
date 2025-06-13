from abc import ABC, abstractmethod
from typing import Any

class BenchmarkReporter(ABC):
    @abstractmethod
    def report(self, file_name: str, data: Any):
        """Process and output benchmark results."""
        pass