# OpenAI Grammar Checker

OpenAI Grammar Checker is a project designed to leverage AI for grammar and spelling correction. It uses OpenAI's language models to analyze and improve text input, ensuring clarity and correctness.

## Features

- ✅ Grammar correction using OpenAI models (eg. GPT-3.5 / GPT-4)
- ✅ CLI interface for interactive use or benchmark testing
- ✅ FastAPI-based web API
- ✅ MongoDB integration for saving results
- ✅ Logging and environment configuration
- ✅ Unit tests with `pytest`
- ✅ Integration tests with `pytest`
- ✅ Prompt templating system
- 🔄 Retry logic and validation (WIP)
- 🧪 Test case runner with structured input/output


## 📦 Project Structure

```
.
├── cli.py               # Entry point (CLI/API/runner)
├── benchmark.py         # Runs benchmark test cases in batch
├── interactive.py       # CLI-based grammar checker
├── api.py               # FastAPI app (WIP)
├── start_mongo.py       # Starts MongoDB subprocess
├── grammar_checker/
│   ├── prompt_builder.py   # Builds prompts for OpenAI
│   ├── openai_client.py    # OpenAI API client wrapper
│   ├── grammar_checker.py  # Core logic for API calls
│   ├── evaluator.py        # Compares actual vs expected output
│   ├── db.py               # MongoDB handler
│   ├── config.py           # Central config (env and defaults)
│   ├── logger.py           # Logging utility
│   └── utils.py            # Utility functions
├── reporting/ 
│   ├── base_reporter.py       # Abstract base class or interface for reporters
│   ├── csv_reporter.py        # Concrete CSV reporter implementation
│   ├── data_access.py         # Data querying/loading utilities
│   ├── factory.py             # Factory to build reporters and/or reports
│   ├── mistakes_report.py     # Logic for generating mistakes report
│   ├── report_runner.py       # Main runner function(s) to execute reports
│   └── sentences_report.py    # Logic for generating sentences report
├── tests/          # Pytest test cases (unit/integration)
├── prompts/
├── models/
│   ├── request.py
│   └── response.py 
├── .env            # Environment configuration
├── requirements.txt
├── pyproject.toml
└── README.md
```


## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/openai_grammar_checker.git
cd openai_grammar_checker
```
2. Create and activate virtual env:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Set up your .env
```bash
cp .env.example .env
# Edit with your OpenAI key and MongoDB URI
```

## Usage

This project provides a command-line interface (CLI) to run the grammar checker in different modes:

```bash
python cli.py <mode-command> --help
```

### Commands 
1. Start API Server
```bash
python cli.py run-api --help
```
2. Interactive Mode
Input text directly and receive grammar improvement suggestions:
```bash
python cli.py interactive --help
```
3. Run Benchmark
Test the performance of different models and prompt templates:
```bash
python cli.py benchmark --help
```
4. Run Reports
Run benchmark reports for specified run IDs:
```bash
python cli.py report --help
```

## Requirements

- Python 3.12 or higher
- OpenAI API key
- MongoDB (local or Atlas)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
