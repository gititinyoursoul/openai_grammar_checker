from pathlib import Path
import pandas as pd
from .base_reporter import BenchmarkReporter
from grammar_checker.logger import get_logger, log_path
from grammar_checker.config import REPORTS_DIR


logger = get_logger(__name__)


class CSVReporter(BenchmarkReporter):
    def __init__(self, output_dir: str = REPORTS_DIR):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def report(self, file_name: str, data):
        file_path = self.output_dir / f"{file_name}.csv"

        if isinstance(data, pd.DataFrame):
            data.to_csv(file_path, index=False)
            logger.info(f"Report {file_name}.csv saved in '{log_path(REPORTS_DIR)}'.")
        else:
            raise TypeError(f"CSVReporter cannot handle data type: {type(data)}")
