import pandas as pd
from reporting.base_reporter import BenchmarkReporter
from grammar_checker.logger import get_logger, get_display_path


logger = get_logger(__name__)


class CSVReporter(BenchmarkReporter):
    extension = "csv"

    def __init__(self):
        super().__init__()

    def report(self, file_name: str, data: pd.DataFrame):
        file_path = self._make_file_path(file_name)

        if isinstance(data, pd.DataFrame):
            data.to_csv(file_path, index=False)
            logger.info(f"Report {file_path.name} saved in '{get_display_path(file_path.parent)}'.")
        else:
            error_msg = f"CSVReporter cannot handle data type: {type(data)}"
            logger.error(error_msg)
            raise TypeError(error_msg)
