from typing import List
from grammar_checker.logger import get_logger
from reporting.data_access import query_benchmark_data
from reporting.factory import ReportType, ReporterType


logger = get_logger(__name__)


def run_reports(run_ids: List[str], reports: List[ReportType], reporter_type: ReporterType) -> None:
    """
    Query benchmark data for given run IDs and run specified reports using the given reporter.

    Args:
        run_ids: List of benchmark run IDs to query data for.
        reports: List of report types to generate.
        reporter: Reporter instance to handle report output.
    """
    reporter = reporter_type.build()
    raw_data = query_benchmark_data(run_ids)

    if not raw_data:
        logger.warning(f"No benchmark data found for {run_ids}. Skipping report generation.")
        return

    for report in reports:
        try:
            report.run(raw_data, reporter)
        except Exception as e:
            logger.error(f"Failed to run report {report.value}: {e}")
