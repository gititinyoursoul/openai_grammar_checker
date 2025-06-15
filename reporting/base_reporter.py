from abc import ABC, abstractmethod
from typing import Any
from pathlib import Path
from datetime import datetime as dt
from grammar_checker.config import REPORTS_DIR


class BenchmarkReporter(ABC):
    extension = "txt"

    def __init__(self, output_dir: Path = REPORTS_DIR):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _make_file_path(self, file_name: str) -> Path:
        """Generate a timestamped file path in the output directory."""
        timestamp = dt.now().strftime("%Y%m%d%H%M%S")
        full_name = f"{timestamp}_{file_name}.{self.extension}"
        return self.output_dir / full_name

    @abstractmethod
    def report(self, file_name: str, data: Any):
        """Process and output benchmark results."""
        pass
