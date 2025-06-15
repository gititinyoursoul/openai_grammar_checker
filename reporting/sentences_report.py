import pandas as pd
from grammar_checker.logger import get_logger
from reporting.data_access import query_benchmark_data
from reporting.base_reporter import BenchmarkReporter
from reporting.csv_reporter import CSVReporter

logger = get_logger(__name__)


def transform_data(raw_data):
    rows = []

    for doc in raw_data:
        row = {
            "run_id": doc.get("benchmark_eval", {}).get("run_id"),
            "test_id": doc.get("benchmark_eval", {}).get("test_id"),
            "model": doc.get("request", {}).get("model"),
            "prompt_version": doc.get("request", {}).get("prompt_version"),
            "actual_sentence": doc.get("response", {}).get("corrected_sentence"),
            "expected_sentence": doc.get("benchmark_eval", {}).get("corrected_sentence"),
        }
        rows.append(row)

    return pd.DataFrame(rows)


def add_sentence_match_column(df):
    df["is_match"] = df["actual_sentence"] == df["expected_sentence"]
    return df


def generate_summary(df):
    summaries = {}

    for run_id in df["run_id"].unique():
        df_run = df[df["run_id"] == run_id]
        cols = ["run_id", "model", "prompt_version"]

        df_summary = (
            df_run.groupby(cols)["is_match"].value_counts().unstack("is_match").fillna(0).astype(int).reset_index()
        )
        df_summary = df_summary.rename(columns={True: "match", False: "not_match"})
        df_summary = df_summary[cols + ["match", "not_match"]].sort_values(by=cols)

        summaries[run_id] = df_summary

    return summaries


def generate_sentence_report(raw_data, reporter: BenchmarkReporter):
    df = transform_data(raw_data)
    df = add_sentence_match_column(df)

    # save detailed view as a CSV file
    for run_id in df["run_id"].unique():
        df_run = df[df["run_id"] == run_id]
        file_name = f"matching_sentences_details_{run_id}"
        reporter.report(file_name, df_run)

    # sentences summary View
    summary_dict = generate_summary(df)

    for run_id, df in summary_dict.items():
        file_name = f"matching_sentences_summary_{run_id}"
        reporter.report(file_name, df)


if __name__ == "__main__":
    run_ids = ["16fb0eb9-b593-4c9e-81cb-78f69373ec07"]  # TODO: pass as args
    raw_data = query_benchmark_data(run_ids)
    reporter = CSVReporter() #TODO: arg
    generate_sentence_report(raw_data, reporter)
