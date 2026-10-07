# AI Code Reviewer

> Formerly **Code Review Agent** (`code-review-agent`). The Python package was renamed from `src/code_review_agent` to `src/ai_code_reviewer`; see [Project Structure](#project-structure).

AI Code Reviewer leverages Large Language Models (LLMs) like **Google's Gemini** and **OpenAI's GPT** to automate code reviews on GitLab Merge Requests. It also provides key insights into your project's CI/CD activity, including DORA metrics, recent pipelines, and merged MRs.

## Key Features

*   **Multi-LLM Code Review**:
    *   Get automated code reviews on any Merge Request using either **Google Gemini** or **OpenAI GPT**.
    *   Publish the generated review directly as a comment on the Merge Request.
*   **CI/CD & Project Insights**:
    *   **Merged MRs**: Fetch a list of merged Merge Requests within a specific timeframe, with optional filtering by labels.
    *   **Recent Pipelines**: Retrieve a summary of recent CI/CD pipelines for your project.
    *   **DORA Metrics**: Calculate "Deployment Frequency" and "Change Failure Rate" to measure your team's DevOps performance.
*   **Flexible & User-Friendly**:
    *   **Dual-Mode CLI**: Use the fully interactive menu for guided workflows or the non-interactive, flag-based mode for automation and scripting.
    *   **Unified Project Configuration**: Set a default project path via the `GITLAB_PROJECT_PATH` environment variable to streamline all commands.
    *   **Multiple Output Formats**: Get data in `table`, `json`, or `csv` format.

## How it Works

1.  **Run the Agent**: Execute the agent with a specific command and flags (e.g., `python main.py review-mr --mr-iid 123 --llm openai --publish`) or run it with no arguments (`python main.py`) to enter the interactive menu.
2.  **Provide Input**: The agent checks for required information, such as a project path or MR IID. If anything is missing, it prompts for it interactively.
3.  **Connect to APIs**: It uses the GitLab API to fetch project data and the appropriate LLM API (Gemini or OpenAI) to perform analysis.
4.  **Process and Display**: The agent processes the data and displays the output in the requested format. For reviews, it gives you the option to post the results directly to GitLab.

## Usage

The agent can be run in two modes: non-interactive (with flags) or interactive (with prompts).

### Non-Interactive Mode (for Automation)

Run commands directly with flags. Ideal for scripts and CI/CD pipelines.

#### **1. Review a Merge Request**

```bash
# Review MR 123 using Gemini and publish the comment
python main.py review-mr --mr-iid 123 --publish

# Review a specific MR URL using OpenAI (does not publish by default)
python main.py review-mr --mr-url "https://gitlab.com/group/project/-/merge_requests/456" --llm openai

# Combine all options
python main.py review-mr --mr-url "https://gitlab.com/group/project/-/merge_requests/456" --llm openai --publish
```

#### **2. Get Merged Merge Requests**

```bash
# Get MRs merged in the last 30 days for the default project
python main.py get-merged-mrs --days 30

# Get MRs with the 'backend' label merged in the last 15 days for a specific project
python main.py get-merged-mrs --project-path "group/project" --days 15 --label "backend" --output-format json
```

#### **3. Get Recent Pipelines**

```bash
# Get pipelines from the last 7 days for the default project
python main.py get-pipelines --days 7

# Get pipelines for a specific project
python main.py get-pipelines --project-path "group/project"
```

#### **4. Calculate DORA Metrics**

Calcula as métricas DORA "Deployment Frequency" e "Change Failure Rate" com base nos jobs de pipeline chamados `Deploy master` (configurável via a variável de ambiente `DEPLOY_JOB_NAME`).

```bash
# Calculate Deployment Frequency for the default project in September
python main.py dora-metrics --metric deployment-frequency --start-date 2024-09-01 --end-date 2024-09-30

# Calculate Change Failure Rate for a specific project and output as CSV
python main.py dora-metrics --project-path "group/project" --metric change-failure-rate --start-date 2024-09-01 --end-date 2024-09-30 --output-format csv

# You can combine all options
python main.py dora-metrics --project-path "group/project" --metric deployment-frequency --start-date 2024-09-01 --end-date 2024-09-30 --output-format json
```

### Interactive Mode (for Convenience)

Run the agent without any arguments to enter a user-friendly interactive menu.

```bash
python main.py
```

The agent will then guide you with prompts for each action:

1.  **Review a Merge Request**:
    *   Prompts for the MR URL.
    *   If `OPENAI_API_KEY` is set, it asks you to choose between Gemini and OpenAI.
    *   After generating the review, it asks if you want to publish it as a comment.
2.  **Get Recent Pipelines**:
    *   Prompts for the project path (if not set in `.env`) and the number of days.
3.  **Get DORA Metrics**:
    *   Prompts for the metric type, project path, start/end dates, and output format.
4.  **Get Merged Merge Requests**:
    *   Prompts for the project path, number of days, and optionally lets you choose from a list of available project labels.

## Getting Started

### Prerequisites

*   Python 3.8+
*   A GitLab account with API access to the project you want to analyze.

### Installation and Configuration

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/brunousml/ai-code-reviewer.git
    cd ai-code-reviewer
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    Copy the example `.env.example` file to `.env`:
    ```bash
    cp .env.example .env
    ```
    Now, open the `.env` file and add your credentials. This file is ignored by Git to keep your secrets safe.

## Configuration

The agent is configured through environment variables in the `.env` file.

*   `GITLAB_URL`: The base URL of your GitLab instance (e.g., `https://gitlab.com`).
*   `GITLAB_PRIVATE_TOKEN`: Your GitLab Personal Access Token. **Required**.
    *   **Permissions**: The token must have the `api` scope.
*   `OPENAI_API_KEY`: Your OpenAI API key. **Optional**.
    *   Required only if you want to use OpenAI models for code reviews. If not provided, this option will be hidden.
*   `GITLAB_PROJECT_PATH`: The default project path (e.g., `group/subgroup/project`). **Optional**.
    *   When set, this path is used as the default for all commands, simplifying execution.
*   `LOG_LEVEL`: The logging level. Defaults to `INFO`. **Optional**.
*   `GITLAB_RETRY_MAX_ATTEMPTS`: Maximum number of retry attempts when posting comments (default: 5). **Optional**.
*   `GITLAB_RETRY_BASE_DELAY`: Base delay in seconds for exponential backoff (default: 1.0). **Optional**.
*   `GITLAB_RETRY_MAX_DELAY`: Maximum delay in seconds, caps the exponential backoff (default: 60.0). **Optional**.
*   `GITLAB_THROTTLE_DELAY`: Fixed delay in seconds between successful API calls (default: 0.5). **Optional**.

## Review Behavior

When publishing a review to GitLab:

*   **Multiple Comments**: The review is automatically split into separate comments based on section separators (`---`). Each section becomes an individual comment on the Merge Request.
*   **All Comments Include Metadata**: Every comment includes the bot identifier (`<!-- agent-review-bot -->`) and signature (configurable via `AGENT_REVIEW_SIGNATURE`, default `Generated by AI with ❤️`).
*   **Automatic Retry**: If rate limiting occurs, the system automatically retries with exponential backoff and respects the `Retry-After` header from GitLab.
*   **Throttling**: A small delay (0.5s by default) is added between successful comment posts to avoid overwhelming the API.
*   **Local Storage**: The complete review is always saved as a single unified file locally, regardless of how it's split when published.

> **Note on the rename:** the bot identifier `<!-- agent-review-bot -->` and the `agent-review-requested` label kept their original names. Merge Requests reviewed before the rename are still recognized and are not reviewed again.

## Project Structure

The code lives in the `src/ai_code_reviewer/` package and follows Clean Architecture:

```
src/ai_code_reviewer/
├── domain/          # Entities, ports (VCS, LLM, storage, cache), and the review parser
├── application/     # Use cases: review_mr, get_pipelines, get_dora_metrics, ...
├── infrastructure/  # Adapters: GitLab, Gemini, OpenAI, file cache, local storage
└── presentation/    # CLI and output formatters
```

`main.py` is the composition root: it creates the services and connects them to the use cases. Imports use the `src.ai_code_reviewer` prefix, so run commands from the repository root.

## Running Tests

The project uses `pytest` for testing. To run the test suite:

### Prerequisites

Make sure you have installed all dependencies:

```bash
pip install -r requirements.txt
```

### Running All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with detailed output showing print statements
pytest -v -s
```

### Running Specific Test Files

```bash
# Run tests for a specific module
pytest tests/application/use_cases/test_review_mr.py

# Run tests for domain services
pytest tests/domain/services/

# Run tests for infrastructure
pytest tests/infrastructure/vcs/
```

### Running Specific Tests

```bash
# Run a specific test function
pytest tests/application/use_cases/test_review_mr.py::test_execute_cache_miss

# Run tests matching a pattern
pytest -k "test_publish_review"
```

### Test Coverage

```bash
# Install pytest-cov if not already installed
pip install pytest-cov

# Run tests with coverage report
pytest --cov=src/ai_code_reviewer --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

### Test Structure

The test suite follows the project structure:

```
tests/
├── application/
│   └── use_cases/
│       ├── test_review_mr.py          # Tests for ReviewMRUseCase
│       ├── test_review_mr_force.py    # Forced re-review (env var / label)
│       └── test_review_mr_skip.py     # Skips MRs already reviewed
├── domain/
│   └── services/
│       └── test_review_parser.py      # Tests for ReviewParser
└── infrastructure/
    └── vcs/
        └── test_gitlab_service_retry.py  # Tests for GitLabService retry logic
```

## Licença e créditos

Código sob licença MIT (veja `LICENSE`). Este projeto inclui o catálogo de code smells de Marcel Jerzyk ([Luzkan/smells](https://github.com/Luzkan/smells), MIT) e a documentação [Google Engineering Practices](https://github.com/google/eng-practices) (© Google LLC, CC BY 3.0). Detalhes em `THIRD_PARTY_NOTICES.md`.
