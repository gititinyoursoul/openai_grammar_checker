import pandas as pd
from difflib import SequenceMatcher
from grammar_checker.logger import get_logger
from reporting.data_access import query_benchmark_data
from reporting.base_reporter import BenchmarkReporter
from reporting.csv_reporter import CSVReporter 


logger = get_logger(__name__)


def fuzzy_match_score(v1, v2):
    if not v1 or not v2:
        return 0.0
    if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
        return 1.0 if abs(v1 - v2) < 0.01 else 0.0
    if isinstance(v1, str) and isinstance(v2, str):
        return SequenceMatcher(None, v1, v2).ratio()

    return 1.0 if v1 == v2 else 0.0


def compare_dicts_keys(source_index, source_item, target_index, target_item, threshold=0.8):
    result = []
    for key in source_item:
        if key in target_item:
            val_a = source_item[key]
            val_b = target_item[key]
            score = fuzzy_match_score(val_a, val_b)
            is_match = score >= threshold
            result.append((source_index, target_index, key, val_a, val_b, score, is_match))
        else:
            result.append((source_index, target_index, key, source_item[key], None, 0.0, False))

    for key in target_item:
        if key not in source_item:
            val_b = target_item[key]
            result.append((source_index, target_index, key, None, val_b, 0.0, False))
    return result


def evaluate_mistakes(actual: list, expected: list, threshold: float = 0.8):
    """
    Evaluate the actual results against expected results.

    :param actual: List of actual results.
    :param expected: List of expected results.
    :param threshold: Similarity threshold for fuzzy matching.
    :return: Detailed evaluation results.
    """
    if not isinstance(actual, list) or not isinstance(expected, list):
        raise ValueError("Both actual and expected should be lists.")

    detailed_results = []

    for index_a, item_a in enumerate(actual):
        for index_b, item_b in enumerate(expected):
            detailed_results.extend(compare_dicts_keys(index_a, item_a, index_b, item_b, threshold))

    return detailed_results


def generate_mistakes_comparison_data(raw_data, treshhold=0.8):
    rows = []

    for doc in raw_data:
        actual_mistakes = doc.get("response", {}).get("mistakes", [])
        expected_mistakes = doc.get("benchmark_eval", {}).get("mistakes", [])

        mistakes = evaluate_mistakes(actual_mistakes, expected_mistakes, treshhold)

        if not mistakes:
            continue

        # run_metadata
        run_id = doc.get("benchmark_eval", {}).get("run_id")
        test_id = doc.get("benchmark_eval", {}).get("test_id")
        prompt_version = doc.get("request", {}).get("prompt_version")
        model = doc.get("request", {}).get("model")

        for mistake in mistakes:
            row = (run_id, test_id, prompt_version, model, *mistake)
            rows.append(row)

    cols = [
        "run_id",
        "test_id",
        "prompt_version",
        "model",
        "source_index",
        "target_index",
        "key",
        "source_value",
        "target_value",
        "fuzzy_score",
        "is_match",
    ]

    return pd.DataFrame(rows, columns=cols)


def generate_mistakes_summary(df):
    summaries = {}

    for run_id in df["run_id"].unique():
        # create df_total / calc total counts
        cols = ["model", "prompt_version"]
        df_total = df.groupby(cols).agg(match_rate=("is_match", "mean"))

        df_total["key"] = "total"
        df_total.set_index("key", append=True, inplace=True)

        # create df_summary
        cols = ["model", "prompt_version", "key"]
        df_summary = df.groupby(cols).agg(
            match_rate=("is_match", "mean"),
        )

        # concat summary and total
        df_summary = pd.concat([df_summary, df_total])
        df_summary = df_summary.unstack("key")

        # rename columns
        new_cols = [f"{col1}_{col2}" for col1, col2 in df_summary.columns]
        df_summary.columns = new_cols

        # sort column
        new_column_order = ["match_rate_original", "match_rate_corrected", "match_rate_type", "match_rate_total"]

        summaries[run_id] = df_summary[new_column_order].reset_index()

    return summaries


def generate_mistakes_report(raw_data, reporter: BenchmarkReporter):
    df = generate_mistakes_comparison_data(raw_data)

    # detailed report
    for run_id in df["run_id"].unique():
        # save detailed view as a CSV file
        df_run = df[df["run_id"] == run_id]
        file_name = f"matching_mistakes_details_{run_id}"
        reporter.report(file_name, df_run)

    # summary report
    summary_dict = generate_mistakes_summary(df)

    for run_id, df in summary_dict.items():
        file_name = f"matching_mistakes_summary_{run_id}"
        reporter.report(file_name, df)



if __name__ == "__main__":
    run_ids = ["16fb0eb9-b593-4c9e-81cb-78f69373ec07"]  # TODO: pass as args
    raw_data = query_benchmark_data(run_ids)
    reporter = CSVReporter() # TODO: pass as args
    generate_mistakes_report(raw_data, reporter)
