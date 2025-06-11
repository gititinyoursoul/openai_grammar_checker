from grammar_checker.logger import get_logger, log_path
from grammar_checker.config import REPORTS_DIR

logger = get_logger(__name__)


def save_dataframe_as_csv(df, file_name):
    file_path = REPORTS_DIR / file_name

    if file_path.exists():
        df.to_csv(file_path, index=False)
        logger.info(f"Report {file_name} saved in {log_path(REPORTS_DIR)}.")
