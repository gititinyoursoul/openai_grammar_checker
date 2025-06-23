# reporting/factory.py
from enum import Enum
from grammar_checker.logger import get_logger
from reporting.sentences_report import generate_sentence_report
from reporting.mistakes_report import generate_mistakes_report
from reporting.csv_reporter import CSVReporter


logger = get_logger(__name__)


class ReportType(str, Enum):
    SENTENCES = "sentences"
    MISTAKES = "mistakes"

    def run(self, data, reporter):
        mapping = {
            ReportType.SENTENCES: generate_sentence_report,
            ReportType.MISTAKES: generate_mistakes_report,
        }

        fn = mapping.get(self)
        return fn(data, reporter)


class ReporterType(str, Enum):
    CSV = "csv"

    def build(self):
        mapping = {
            ReporterType.CSV: CSVReporter,
        }

        cls = mapping.get(self)
        return cls()
