# OpenAI Grammar Checker

OpenAI Grammar Checker is a project designed to leverage AI for grammar and spelling correction. It uses OpenAI's language models to analyze and improve text input, ensuring clarity and correctness.

## Features

- ✅ Grammar correction using OpenAI models (GPT-3.5 / GPT-4)
- ✅ CLI interface for interactive use or benchmark testing
- ✅ FastAPI-based web API
- ✅ MongoDB integration for saving results
- ✅ Logging and environment configuration
- ✅ Unit tests with `pytest`
- ✅ Prompt templating system
- 🔄 Retry logic and validation (WIP)
- 🧪 Test case runner with structured input/output


## 📦 Project Structure

```
.
├── main.py              # Entry point (CLI/API/runner)
├── runner.py            # Runs test cases in batch
├── interactive.py       # CLI-based grammar checker
├── api.py               # FastAPI app (WIP)
├── start_mongo.py       # Starts MongoDB subprocess
├── grammar_checker/
│   ├── prompt_builder.py  # Builds prompts for OpenAI
│   ├── openai_client.py   # OpenAI API client wrapper
│   ├── grammar_checker.py # Core logic for API calls
│   ├── evaluator.py       # Compares actual vs expected output
│   ├── db.py              # MongoDB handler
│   ├── config.py          # Central config (env and defaults)
│   ├── logger.py          # Logging utility
│   └── utils.py           # Utility functions
├── tests/               # Pytest test cases
├── .env                 # Environment configuration
├── requirements.txt
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
source venv/bin/activate  # Windows: venv\Scripts\activate
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
python cli.py run-api

```
2. Interactive Mode
Input text directly and receive grammar improvement suggestions:
```bash
python cli.py interactive
```
3. Run Benchmarks
Test the performance of different models and prompt templates:
```bash
python cli.py benchmarks
```

## Requirements

- Python 3.12 or higher
- OpenAI API key
- MongoDB (local or Atlas)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
