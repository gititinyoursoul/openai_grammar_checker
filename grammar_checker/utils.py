import json
import os

# load test cases from a json file
def load_test_cases(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Test cases file not found: {file_path}")
    with open(file_path, "r") as file:
        return json.load(file)

# save test results to a json file
def save_test_results(file_path, results):
    with open(file_path, "w") as file:
        json.dump(results, file, indent=4)
    print(f"Test results saved to {file_path}")
    

