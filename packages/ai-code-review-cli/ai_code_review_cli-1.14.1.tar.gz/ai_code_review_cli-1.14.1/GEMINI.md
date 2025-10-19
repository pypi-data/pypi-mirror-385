# Project Overview

This project is a command-line tool named "AI Code Review" that provides AI-powered code analysis. It can be used to review local changes, analyze remote pull/merge requests, and integrate with CI/CD pipelines. The tool is written in Python and uses the `click` library for its command-line interface. It supports multiple AI providers, including Gemini, Anthropic, and Ollama, and is highly configurable through a combination of CLI arguments, environment variables, and a YAML configuration file.

The project is composed of two main scripts:
- `ai-code-review`: The main script that performs the code review.
- `ai-generate-context`: A script that analyzes the project and generates a context file (`.ai_review/project.md`) to provide more information to the AI model during the review process.

## High-Level Architecture

The tool is designed with a modular architecture that separates concerns and allows for extensibility. The main components are:

- **CLI**: The command-line interface, built with `click`, which parses arguments and orchestrates the different workflows.
- **Configuration System**: A Pydantic-based system that handles configuration from multiple sources (CLI arguments, environment variables, and a YAML file) with a clear priority order.
- **Platform Factory**: A factory that creates the appropriate platform client (GitLab, GitHub, or Local Git) based on the configuration.
- **Review Engine**: The core component that orchestrates the review process, from fetching the diff to generating the review and posting it to the platform.
- **AI Provider Abstraction**: A LangChain-based abstraction layer that provides a unified interface for interacting with different AI models (Gemini, Anthropic, Ollama).
- **Prompt Management**: A system for managing and rendering prompt templates for different review formats.

## Workflows

The tool supports three main workflows:

1.  **Local Code Review**: This workflow allows developers to review their local changes before committing or pushing them. It compares the current state of the repository with a target branch and generates a review in a terminal-friendly format.
2.  **Remote Code Review**: This workflow analyzes existing merge/pull requests from GitLab or GitHub. It can be run from the command line to get a review of a specific MR/PR, and it can also post the review as a comment on the platform.
3.  **CI/CD Integration**: This workflow integrates the tool into a CI/CD pipeline (GitLab CI or GitHub Actions) to automatically review merge/pull requests.

# Building and Running

## Installation

To install the project and its dependencies, you can use `uv` or `pip`:

```bash
# Install using uv (recommended)
uv sync

# Or with pip
pip install -e .
```

## Running the tool

The project provides two command-line scripts:

### `ai-code-review`

This script is used to perform the code review. It can be used in three different modes:

- **Local Review**: Reviews local changes against a target branch.
- **Remote Review**: Reviews a pull/merge request on a remote repository (GitLab or GitHub).
- **CI/CD Integration**: Can be integrated into a CI/CD pipeline to automatically review pull/merge requests.

### `ai-generate-context`

This script analyzes the project and generates a context file that can be used by the `ai-code-review` script to improve the quality of the reviews.

```bash
# Generate context for the current project
ai-generate-context .
```

## Testing

The project uses `pytest` for testing. To run the tests, you can use the following command:

```bash
pytest
```

# Development Conventions

The project follows standard Python development conventions. It uses `ruff` for linting and formatting, and `mypy` for static type checking. The configuration for these tools can be found in the `pyproject.toml` file.

- **Linting**: `ruff check .`
- **Formatting**: `ruff format .`
- **Type Checking**: `mypy .`