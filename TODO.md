# ✅ AI Grammar Tool – TODO List

---

## 🔧 Core Improvements

- [x] Refactor `prompt_builder`
- [x] Read instruction from file
- [ ] Change test cases JSON structure: keys "input", "expected": ["mistakes", "corrected_sentence"]
- [ ] Better output summaries / simple report
- [ ] Validation of OpenAI responses with Pydantic
- [ ] Refactor `runner.py`: convert save_results into function
- [ ] Use a small task runner like Typer or Click
- [ ] Parallel execution via `ThreadPoolExecutor`

---

## ✅ CLI Features

- [x] Modify `parse_arguments` to support user input
- [x] Add logic to `main()` to handle input/test modes
- [x] Create `interactive.py` with CLI input and feedback loop
- [x] Add MongoDB storage for results

---

## 🧪 Testing

- [x] Unit tests for modules
  - [x] `grammar_checker.py`
  - [x] `db.py`
  - [x] `openai_client.py`
  - [x] `prompt_builder.py`
  - [x] `utils.py`
  - [x] `loggger.py`
  - [ ] `start_mongo.py`
- [ ] integration tests for entry points
  - [x] runner.py
  - [ ] interactive.py
  - [x] main.py
  - [ ] update test_main.py with new logic


---

## ⚙️ Configuration & Environment

- [x] Load `.env` using `load_dotenv()`
- [ ] Add `reload=True` to `.env` for dev mode
- [ ] Use consistent config for URI, host, and port

---

## 🟡 Mid-Term (1–2 Days)

- [x] Extend CLI with model selection and modes
- [x] Expand MongoDB schema:
  - Timestamp
  - Model used
  - User identifier (future)
- [x] Add mock tests for OpenAI responses


---

## 🌐 API Improvments

- [ ] Split FastAPI code into router + app
- [ ] Retry logic for API calls
- [ ] Add response models
- [ ] Improve error handling
- [ ] Add basic rate limiting or auth
- [ ] Log Mongo result ID
- [x] Validation: reject empty sentence
- [ ] Separate `admin_api.py` for CRUD ops

---

## 🧹 Logging Tasks

- [x] Add logging to all modules
- [ ] Deactivate debug logs in CLI output
- [ ] Enable debug mode through CLI (explicit args)
- [ ] Improve logging modes: debug mode and info

---

## 🔵 Long-Term Goals

- [ ] Build REST API with **FastAPI**
  - [ ] `POST /check-grammar`
  - [ ] `GET /logs`
- [ ] Add authentication (JWT or API key)
- [ ] Deployment:
  - [ ] Dockerize the app
  - [ ] Deploy to Render / Vercel / AWS
- [ ] Monitoring: logs, Sentry, Mongo, etc.
