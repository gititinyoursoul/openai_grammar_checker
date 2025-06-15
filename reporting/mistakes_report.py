from dotenv import load_dotenv

load_dotenv()
from typing import List, Dict
import pandas as pd
from difflib import SequenceMatcher
from grammar_checker.logger import get_logger
from reporting.data_access import query_benchmark_data
from reporting.base_reporter import BenchmarkReporter
from reporting.csv_reporter import CSVReporter


logger = get_logger(__name__)


def fuzzy_match_score(v1, v2):
    """
    Calculates a fuzzy match score between two values.
    Returns a float between 0.0 and 1.0 indicating the similarity between v1 and v2.
    Supports numeric and string comparisons; uses SequenceMatcher for strings.
    """
    if not v1 or not v2:
        return 0.0
    if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
        return 1.0 if abs(v1 - v2) < 0.01 else 0.0
    if isinstance(v1, str) and isinstance(v2, str):
        return SequenceMatcher(None, v1, v2).ratio()

    return 1.0 if v1 == v2 else 0.0


def compare_dicts_keys(
    source_index: int, source_item: Dict, target_index: int, target_item: Dict, threshold: float
) -> List[tuple]:
    """
    Compares the keys and values of two dictionaries and returns a list of tuples containing comparison results.
    Args:
        source_index (int): Index or identifier for the source dictionary.
        source_item (Dict): The source dictionary to compare.
        target_index (int): Index or identifier for the target dictionary.
        target_item (Dict): The target dictionary to compare.
        threshold (float): The minimum fuzzy match score to consider values as matching.
    Returns:
        List[tuple]: A list of tuples, each containing:
            (source_index, target_index, key, source_value, target_value, score, is_match)
        where 'score' is the fuzzy match score and 'is_match' is a boolean indicating if the score meets the threshold.
    """
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


def evaluate_mistakes(actual: list, expected: list, threshold: float):
    """Compares actual and expected lists of mistakes using fuzzy matching."""
    if not isinstance(actual, list) or not isinstance(expected, list):
        raise ValueError("Both actual and expected should be lists.")

    detailed_results = []

    for index_a, item_a in enumerate(actual):
        for index_b, item_b in enumerate(expected):
            detailed_results.extend(compare_dicts_keys(index_a, item_a, index_b, item_b, threshold))

    return detailed_results


def transform_data(raw_data: List[Dict], treshhold: float = 0.8) -> pd.DataFrame:
    """
    Generates a DataFrame comparing actual and expected mistakes from evaluation data.
    Args:
        raw_data (List[Dict]): List of documents containing actual and expected mistakes, along with metadata.
        treshhold (float, optional): Fuzzy matching threshold for mistake comparison. Defaults to 0.8.
    Returns:
        pd.DataFrame: DataFrame with comparison results and associated metadata for each mistake.
    """

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


def generate_summary(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Generates a summary of match rates for each run in the given DataFrame.
    For each unique 'run_id', computes the mean 'is_match' rate grouped by
    'model', 'prompt_version', and 'key', as well as overall totals. Returns a
    dictionary mapping each 'run_id' to its corresponding summary DataFrame.
    Args:
        df (pd.DataFrame): Input DataFrame containing columns 'run_id', 'model',
            'prompt_version', 'key', and 'is_match'.
    Returns:
        Dict[str, pd.DataFrame]: Dictionary where keys are 'run_id' values and
            values are summary DataFrames with match rates.
    """
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


def generate_mistakes_report(raw_data: List[Dict], reporter: BenchmarkReporter) -> None:
    """
    Generates detailed and summary reports of mistakes from raw benchmark data.
    This function processes the provided raw data to create a detailed comparison DataFrame,
    then generates and saves a detailed report for each unique run ID. It also creates a summary
    of mistakes and saves a summary report for each run ID.
    Args:
        raw_data (List[Dict]): The raw benchmark data containing information about mistakes.
        reporter (BenchmarkReporter): An object responsible for saving the generated reports.
    Returns:
        None
    """
    df = transform_data(raw_data)
    # detailed report
    for run_id in df["run_id"].unique():
        # save detailed view as a CSV file
        df_run = df[df["run_id"] == run_id]
        file_name = f"mistakes_details_{run_id}"
        reporter.report(file_name, df_run)

    # summary report
    summary_dict = generate_summary(df)

    for run_id, df in summary_dict.items():
        file_name = f"mistakes_summary_{run_id}"
        reporter.report(file_name, df)


if __name__ == "__main__":
    run_ids = ["16fb0eb9-b593-4c9e-81cb-78f69373ec07"]  # TODO: pass as args
    raw_data = query_benchmark_data(run_ids)
    reporter = CSVReporter()  # TODO: pass as args
    generate_mistakes_report(raw_data, reporter)
