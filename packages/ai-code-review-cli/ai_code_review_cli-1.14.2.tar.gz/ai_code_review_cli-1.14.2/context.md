# Project Context for AI Code Review

## Project Overview

**Purpose:** An AI-powered code review tool that analyzes local Git changes and remote pull/merge requests.
**Type:** CLI tool
**Domain:** Developer Tools / Code Quality Automation
**Key Dependencies:** `click` (CLI framework), `langchain` (LLM orchestration), `python-gitlab`/`pygithub` (Git provider APIs)

## Technology Stack

### Core Technologies
- **Primary Language:** Python
- **Framework/Runtime:** Asyncio with aiohttp and Click
- **Architecture Pattern:** Asynchronous, modular architecture using LangChain for LLM orchestration.

### Key Dependencies (for Context7 & API Understanding)
- **langchain>=0.2.0** - The core framework for building LLM-powered applications. Code will heavily use its abstractions like chains, agents, and model integrations. Reviewers must understand LangChain concepts.
- **aiohttp>=3.9.0** - Asynchronous HTTP client/server. All network I/O is likely non-blocking. Reviewers must check for correct `async`/`await` usage and resource management.
- **pydantic>=2.5.0** - Used for data validation, serialization, and configuration management. Code changes will often involve defining or modifying Pydantic models.
- **python-gitlab>=4.0.0** - API client for GitLab. Indicates the application interacts with GitLab repositories, merge requests, or pipelines. Reviewers should check for correct and secure API usage.
- **pygithub>=2.1.0** - API client for GitHub. Indicates the application interacts with GitHub repositories, pull requests, or actions. Reviewers should check for correct and secure API usage.
- **click>=8.1.0** - Defines the application's Command-Line Interface (CLI). Changes to CLI commands, options, and arguments will be implemented using this library.

### Development Tools & CI/CD
- **Testing:** Pytest with pytest-asyncio for asynchronous code, pytest-mock for mocking, and pytest-cov for coverage tracking.
- **Code Quality:** Ruff for linting and formatting, and MyPy for static type checking.
- **Build/Package:** pyproject.toml for managing dependencies and packaging, following modern Python standards.
- **CI/CD:** gitlab-ci - The `.gitlab-ci.yml` file defines a pipeline that likely runs static analysis (Ruff, MyPy) and automated tests (Pytest) on every commit.

## Architecture & Code Organization

### Project Organization
```
.
├── .ai_review/
│   └── project.md
├── docs/
│   ├── context-generator.md
│   ├── developer-guide.md
│   └── user-guide.md
├── src/
│   ├── ai_code_review/
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── base_platform_client.py
│   │   │   ├── github_client.py
│   │   │   ├── gitlab_client.py
│   │   │   ├── local_git_client.py
│   │   │   └── review_engine.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── platform.py
│   │   │   └── review.py
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   ├── anthropic.py
│   │   │   ├── base.py
│   │   │   ├── gemini.py
│   │   │   └── ollama.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── constants.py
│   │   │   ├── exceptions.py
│   │   │   ├── platform_exceptions.py
│   │   │   ├── prompts.py
│   │   │   └── ssl_utils.py
│   │   ├── __init__.py
│   │   └── cli.py
│   └── context_generator/
│       ├── core/
│       │   ├── __init__.py
│       │   ├── code_extractor.py
│       │   ├── context_builder.py
│       │   ├── facts_extractor.py
│       │   └── llm_analyzer.py
│       ├── providers/
│       │   ├── __init__.py
│       │   ├── ci_docs_provider.py
│       │   └── context7_provider.py
│       ├── sections/
│       │   ├── __init__.py
│       │   ├── base_section.py
│       │   ├── ci_docs_section.py
│       │   ├── context7_section.py
│       │   ├── overview_section.py
│       │   ├── review_section.py
│       │   ├── structure_section.py
│       │   └── tech_stack_section.py
│       ├── templates/
│       │   ├── __init__.py
│       │   ├── context_template.md
│       │   └── template_engine.py
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── git_utils.py
│       │   └── helpers.py
│       ├── __init__.py
│       ├── cli.py
│       ├── constants.py
│       └── models.py
├── tests/
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_context_generator_simple.py
│   ├── unit/
│   │   ├── test_ai_code_review_anthropic_provider.py
│   │   ├── test_ai_code_review_base_provider.py
│   │   ├── test_ai_code_review_cli.py
│   │   ├── test_ai_code_review_cli_ci.py
│   │   ├── test_ai_code_review_config.py
│   │   ├── test_ai_code_review_config_file_loading.py
│   │   ├── test_ai_code_review_exceptions.py
│   │   ├── test_ai_code_review_gemini_provider.py
│   │   ├── test_ai_code_review_github_client.py
│   │   ├── test_ai_code_review_gitlab_client.py
│   │   ├── test_ai_code_review_local_git_client.py
│   │   ├── test_ai_code_review_models.py
│   │   ├── test_ai_code_review_ollama_provider.py
│   │   ├── test_ai_code_review_prompts.py
│   │   ├── test_ai_code_review_review_engine.py
│   │   ├── test_ai_code_review_skip_review.py
│   │   ├── test_ai_code_review_ssl_utils.py
│   │   ├── test_context_generator_base.py
│   │   ├── test_context_generator_ci_docs_provider.py
│   │   ├── test_context_generator_ci_docs_section.py
│   │   ├── test_context_generator_cli.py
│   │   ├── test_context_generator_code_extractor.py
│   │   ├── test_context_generator_constants.py
│   │   ├── test_context_generator_context7_models.py
│   │   └── test_context_generator_context7_provider.py
│   ├── __init__.py
│   └── conftest.py
├── web/
├── .gitignore
├── .gitlab-ci.yml
├── .pre-commit-config.yaml
├── Containerfile
├── README.md
└── pyproject.toml
```

### Architecture Patterns
**Code Organization:** Layered Architecture. The application is divided into distinct layers: a Command Line Interface (`cli.py`), a `core` business logic layer (`review_engine.py`), `providers` for external service integrations (LLMs), `models` for data structures (Pydantic-based), and `utils` for shared utilities.
**Key Components:**
- **`ReviewEngine`**: The central orchestrator in `src/ai_code_review/core/review_engine.py`. It initializes and coordinates platform clients and AI providers to execute the code review process.
- **Platform Clients**: A set of classes (`GitHubClient`, `GitLabClient`, `LocalGitClient`) implementing a common `PlatformClientInterface`. This is a Strategy Pattern for interacting with different code hosting platforms.
- **AI Providers**: A set of classes (`Anthropic`, `Gemini`, `Ollama`) inheriting from `BaseAIProvider`. This is a Strategy Pattern for interacting with different Large Language Models.
- **Configuration Models**: Pydantic `BaseSettings` and `BaseModel` classes in `src/ai_code_review/models/config.py` that define, validate, and load all application settings from environment variables and defaults.
**Entry Points:** The primary application entry point is the command-line interface defined in `src/ai_code_review/cli.py`, which uses the `click` library to parse arguments and initiate the `ReviewEngine`. A secondary entry point exists for a separate tool at `src/context_generator/cli.py`.

### Important Files for Review Context
- **`src/ai_code_review/core/review_engine.py`** - Contains the main business logic. Understanding this file is critical to grasp how platform data, AI provider calls, and configuration are orchestrated to generate and post a review.
- **`src/ai_code_review/models/config.py`** - Defines all application configuration using Pydantic. Reviewers must understand this file to assess the impact of changes related to settings, new providers, or validation logic.
- **`src/ai_code_review/cli.py`** - The main entry point. It handles user input, configuration loading, and top-level error handling. Changes here directly affect the user experience and application startup.

### Development Conventions
- **Naming:** Follows PEP 8 standards. `PascalCase` is used for classes (`ReviewEngine`, `Config`) and `snake_case` is used for functions, methods, and variables (`_create_platform_client`). Internal helper functions are prefixed with a single underscore.
- **Module Structure:** The `src` directory contains two distinct top-level Python packages: `ai_code_review` and `context_generator`. Each package is internally organized by feature/layer (`core`, `models`, `providers`, `utils`), promoting high cohesion and low coupling.
- **Configuration:** Configuration is centralized and strongly typed using Pydantic's `BaseSettings` in `src/ai_code_review/models/config.py`. It supports loading from environment variables and uses custom validators (`@field_validator`, `@model_validator`) for complex rules.
- **Testing:** The project uses a standard `tests/` directory, separated into `unit/` and `integration/` subdirectories. Test filenames are prefixed with `test_`, indicating the use of a framework like `pytest`.

## Code Review Focus Areas

- **[LangChain Integration & Prompt Engineering]** - Scrutinize how prompts are constructed (likely in `ai_code_review/utils/prompts.py`) and how the `create_review_chain` function is implemented. Verify that the LangChain Expression Language (LCEL) chains correctly handle inputs and parse outputs from various providers (Ollama, Google, Anthropic). Check for robustness against malformed AI responses and ensure token estimation logic in `review_engine.py` is sound to prevent API errors.

- **[Architecture/Pattern Area: Provider Abstraction]** - The `ReviewEngine` uses factory methods (`_create_platform_client`, `_create_ai_provider`) to abstract platform and AI implementations. When reviewing changes to a specific provider (e.g., `GitLabClient` or `OllamaProvider`), ensure it strictly adheres to its interface (`PlatformClientInterface`, `BaseAIProvider`) and that no provider-specific logic leaks into the core `ReviewEngine`.

- **[Framework-Specific Area: Pydantic Configuration Validation]** - The project relies heavily on `pydantic` and `pydantic-settings` for configuration (`config.py`). Pay close attention to `field_validator` and `model_validator` functions. Ensure they handle all edge cases for combining CLI arguments, environment variables, and file-based settings. Verify that interdependent fields (e.g., provider-specific settings) are validated correctly.

- **[Code Quality Area: Asynchronous Operations and Error Handling]** - The application is built on `asyncio` and uses `aiohttp`/`httpx`. Ensure all I/O operations (API calls to platforms and AI providers) are properly `await`ed and non-blocking. Review exception handling to confirm that specific, custom exceptions like `PlatformAPIError` and `AIProviderError` are caught and handled gracefully, rather than generic `Exception` clauses.

- **[Domain-Specific Area: Diff Processing and Filtering]** - The core domain involves analyzing code diffs. Review the logic that fetches diffs from platform clients and applies filtering based on the patterns in `config.py` (`_DEFAULT_EXCLUDE_PATTERNS`). Verify the logic for handling large diffs (`AUTO_BIG_DIFFS_THRESHOLD_CHARS`) and the conditions that trigger a `ReviewSkippedError` to ensure they align with expected behavior.

## Library Documentation & Best Practices

*Library documentation not available*

## CI/CD Configuration Guide

# CI/CD Recent Changes & Critical Updates

This guide provides focused insights into recent changes, security considerations, and common errors in GitLab CI/CD configuration. It is designed to help AI code reviewers identify outdated patterns, security risks, and potential pipeline failures.

## 1. Recent Changes & New Features (Last 2-3 Years)

This section highlights new keywords and capabilities that may not be present in older training data. Reviewers should recommend these modern features over legacy workarounds.

### Pipeline Inputs for Manual Pipelines (`inputs`)

-   **Introduced:** GitLab 17.11 (GA in 18.1)
-   **Description:** The `inputs` keyword provides a structured and type-safe way to pass parameters to manually triggered pipelines. It is the modern, recommended replacement for using CI/CD variables for user-provided parameters in manual runs. It improves security and clarity over generic variables.
-   **Reviewer Focus:**
    -   Recommend migrating from `variables` with `description` to `spec:inputs` for manual pipelines.
    -   Ensure that input values in the `New pipeline` UI match the expected type defined in the configuration.
    -   Flag any complex logic in scripts that could be simplified by using strongly-typed inputs.

-   **Example Configuration (`.gitlab-ci.yml`):**
    ```yaml
    spec:
      inputs:
        target:
          description: "The deployment target environment."
          type: string
          options:
            - staging
            - production
          default: staging
        run_performance_tests:
          description: "Run performance tests after deployment."
          type: boolean
          default: false

    deploy:
      script:
        - echo "Deploying to $CI_INPUT_TARGET"
        - if [ "$CI_INPUT_RUN_PERFORMANCE_TESTS" == "true" ]; then ./run-perf-tests.sh; fi
      rules:
        - if: $CI_PIPELINE_SOURCE == "web"
    ```

### OIDC Token Integration in `default` (`id_tokens`)

-   **Introduced:** GitLab 16.4
-   **Description:** The `id_tokens` keyword, used for authenticating with third-party services via OIDC, can now be configured globally under the `default` key. This simplifies configuration by avoiding repetition in every job that requires an OIDC token.
-   **Reviewer Focus:**
    -   If multiple jobs define the same `id_tokens` block, recommend moving it to the `default` section to reduce redundancy.
    -   Verify that the `aud` (audience) claim is correctly configured for the target cloud provider (e.g., AWS, GCP, Vault).

-   **Example Configuration:**
    ```yaml
    default:
      id_tokens:
        VAULT_ID_TOKEN:
          aud: https://vault.example.com

    get-secrets-from-vault:
      script:
        - echo "Fetching secrets using token from $VAULT_ID_TOKEN_FILE"
        # Script uses the VAULT_ID_TOKEN to authenticate with Vault

    deploy-to-cloud:
      script:
        - echo "Deploying to cloud..."
        # This job also inherits the id_tokens configuration
    ```

### Fine-Grained Inheritance Control (`inherit`)

-   **Description:** The `inherit` keyword provides explicit control over which global `default` configurations and `variables` a job uses. This is critical for creating exceptions and preventing unintended side effects from global settings.
-   **Reviewer Focus:**
    -   When a job needs to run in a clean environment (e.g., a linting job with no dependencies), check for `inherit: default: false` and `inherit: variables: false`.
    -   For jobs that only need specific global settings, verify the use of array syntax (e.g., `inherit: default: [image, retry]`) to avoid inheriting unnecessary configurations like `before_script`.
    -   Flag jobs that override many default values; they might be candidates for disabling inheritance altogether.

-   **Example Configuration:**
    ```yaml
    default:
      image: ruby:3.0
      before_script:
        - bundle install

    variables:
      RAILS_ENV: test

    lint-job:
      # This job should not run 'bundle install' or use the default image
      inherit:
        default: false
        variables: false
      image: alpine:latest
      script:
        - echo "Running in a clean, minimal environment"

    test-job:
      # This job only needs the default image, not the before_script
      inherit:
        default: [image]
      script:
        - bundle exec rspec
    ```

### Viewing Manual Pipeline Variables in UI

-   **Introduced:** GitLab 17.2 (GA in 18.4)
-   **Description:** A project setting now allows users with the Developer role or higher to view the keys and values of variables passed during a manual pipeline run.
-   **Reviewer Focus:** This is a UI feature, but it has security implications for CI configuration.
    -   **CRITICAL:** If a pipeline can be run manually, strongly advise against passing sensitive credentials (tokens, passwords) as manual variables.
    -   Recommend using **Protected Variables** scoped to protected branches/tags or an external secrets manager like Vault, especially if this UI visibility setting is enabled.

## 2. Deprecated & Removed Features

The provided documentation does not list specific deprecated keywords. However, it highlights modern patterns that effectively supersede older ones. Reviewers should focus on migrating to these new standards.

### `needs` Keyword vs. Stage-Based Execution

-   **Status:** Stage-based execution is not deprecated, but `needs` is the modern approach for building faster, more flexible Directed Acyclic Graph (DAG) pipelines.
-   **Description:** The `needs` keyword allows a job to start as soon as its specified dependencies are complete, regardless of stage ordering. This breaks the rigid sequential execution of stages and can significantly reduce pipeline duration.
-   **Reviewer Focus:**
    -   Identify pipelines with many sequential stages where jobs in later stages do not depend on all jobs in earlier stages.
    -   Recommend replacing the stage-based ordering with `needs` to enable parallel execution and optimize pipeline speed.
    -   Ensure that when `needs` is used, it correctly lists all required dependency jobs. A missing `needs` entry can lead to race conditions or missing artifacts.

-   **Old Pattern (Stage-based):**
    ```yaml
    stages:
      - build
      - test
      - deploy

    build-a:
      stage: build
      script: make a

    build-b:
      stage: build
      script: make b

    test-a:
      stage: test
      script: test a # Depends only on build-a

    test-b:
      stage: test
      script: test b # Depends only on build-b
    ```

-   **Modern Pattern (with `needs`):**
    ```yaml
    stages:
      - build
      - test
      - deploy

    build-a:
      stage: build
      script: make a

    build-b:
      stage: build
      script: make b

    test-a:
      stage: test
      script: test a
      needs: ["build-a"] # Can start as soon as build-a finishes

    test-b:
      stage: test
      script: test b
      needs: ["build-b"] # Can start as soon as build-b finishes
    ```

## 3. Security Updates & Vulnerabilities

Reviewers must be vigilant about how secrets and permissions are handled in `.gitlab-ci.yml`.

### Storing Secrets in `.gitlab-ci.yml`

-   **Status:** **CRITICAL MISCONFIGURATION.**
-   **Description:** The documentation explicitly states that sensitive variables (tokens, keys, passwords) should **never** be stored in the `.gitlab-ci.yml` file. This file is part of the repository and visible to anyone with read access.
-   **Reviewer Focus:**
    -   Immediately flag any hardcoded secrets, tokens, or credentials in the `variables` section or `script` blocks.
    -   Recommend moving all sensitive data to the GitLab UI as CI/CD variables (**Settings > CI/CD > Variables**).
    -   For maximum security, recommend using **Protected** and **Masked** variables.

### Protected and Masked Variables

-   **Description:**
    -   **Protected:** The variable is only available to jobs running on protected branches or protected tags. This prevents it from being exposed in feature branch pipelines or by unauthorized users.
    -   **Masked:** The value of the variable is hidden in job logs. This helps prevent accidental exposure of secrets.
-   **Reviewer Focus:**
    -   For any variable containing a secret, verify if it should be configured as **Protected**. This is essential for deployment keys, API tokens, etc.
    -   Check if sensitive variables are **Masked**. If not, recommend enabling it. Note that masking has limitations and may not work for complex, multi-line values.

### Forked Project Pipeline Security

-   **Description:** By default, pipelines for merge requests from a forked project do not have access to the parent project's CI/CD variables. However, if the pipeline is configured to run in the parent project's context, these variables become available.
-   **Reviewer Focus:**
    -   In projects that accept contributions from forks, carefully review the pipeline configuration for merge requests.
    -   Be aware that running pipelines for forks in the parent project context exposes secrets to potentially untrusted code.
    -   Ensure that any secrets used in these pipelines are appropriately protected and that the scripts do not allow for arbitrary code execution that could exfiltrate them.

## 4. Breaking Changes & Migration Issues

These are subtle issues that can cause unexpected pipeline behavior or failures.

### Unquoted Numeric Variables Parsed as Octal

-   **Description:** The YAML parser (Psych) interprets unquoted numbers with a leading zero (e.g., `012345`) as octal values, not strings. This can corrupt version numbers, identifiers, or secrets.
-   **Reviewer Focus:**
    -   **CRITICAL:** Flag any variable definition where the value is numeric, starts with a zero, and is not enclosed in quotes.
    -   Enforce the best practice of **always quoting variable values** (`"value"` or `'value'`) to ensure they are treated as strings and avoid parsing errors.

-   **Incorrect (Causes Data Corruption):**
    ```yaml
    variables:
      APP_VERSION: 07.1.0  # Parsed incorrectly
      POSTAL_CODE: 01234   # Parsed as octal 668
    ```

-   **Correct (Safe):**
    ```yaml
    variables:
      APP_VERSION: "07.1.0"
      POSTAL_CODE: "01234"
    ```

### Ineffective `default` Keywords

-   **Description:** The documentation notes that due to existing issues, some keywords under `default` do not work as expected.
-   **Reviewer Focus:**
    -   Flag the use of `default:artifacts:expire_in`. This setting has no effect and will not set a default expiration time. It must be defined per-job. (Issue 404563)
    -   Flag the use of `default:timeout`. This setting has no effect. Job timeouts must be configured per-job. (Issue 213634)

-   **Example of Ineffective Configuration:**
    ```yaml
    default:
      # These settings will be ignored by GitLab CI
      timeout: 10m
      artifacts:
        expire_in: 1 day

    my_job:
      script:
        - echo "This job will use the project-level timeout, not 10m."
        - echo "Artifacts will not expire in 1 day unless specified here."
      artifacts:
        paths: [output.txt]
        # expire_in must be defined here to work
        expire_in: 1 day
    ```

## 5. Common Configuration Errors

These are frequent mistakes that lead to pipeline failures or unexpected behavior.

### Using Reserved Keywords as Job Names

-   **Description:** A specific list of top-level keywords cannot be used as job names. Doing so will result in a syntax error or unpredictable behavior.
-   **Reviewer Focus:**
    -   Ensure job names are not one of the following reserved keywords: `image`, `services`, `stages`, `before_script`, `after_script`, `variables`, `cache`, `include`.
    -   The special job `pages:deploy` is only valid when configured for a `deploy` stage.
    -   Advise against using quoted booleans or nulls as job names (e.g., `"true"`, `"false"`, `"nil"`) as it makes the configuration confusing and error-prone.

### Misunderstanding Variable Scope and Precedence

-   **Description:** Variables defined at the job level will always override variables with the same name defined at the global (top) level. A common error is expecting a global variable to be available after a job has overridden it.
-   **Reviewer Focus:**
    -   When a job fails due to a missing or incorrect variable, check if the job defines its own `variables` block that might be overriding a global default.
    -   To completely isolate a job from global variables, check for the use of `variables: {}`.

-   **Example Illustrating Precedence:**
    ```yaml
    variables:
      DEPLOY_SERVER: "staging.example.com"

    deploy_staging:
      script:
        - echo "Deploying to $DEPLOY_SERVER" # Outputs "staging.example.com"

    deploy_production:
      variables:
        DEPLOY_SERVER: "production.example.com" # This overrides the global value
      script:
        - echo "Deploying to $DEPLOY_SERVER" # Outputs "production.example.com"
    ```

### Hiding Jobs Incorrectly

-   **Description:** To temporarily disable a job, its name should be prefixed with a period (e.g., `.my_job`). A common mistake is to assume a hidden job can contain invalid YAML. Hidden jobs are ignored by the pipeline runner but are still parsed and can be used with `extends`, so they must contain valid YAML.
-   **Reviewer Focus:**
    -   Check that any job name starting with a `.` still contains valid YAML key-value pairs, even if it lacks a `script` section. An empty or malformed hidden job can cause a pipeline validation error.

-   **Incorrect (YAML Error):**
    ```yaml
    .disabled_job:
      this is not valid yaml
    ```

-   **Correct:**
    ```yaml
    .disabled_job:
      # This job is disabled but can be used with 'extends'
      retry: 2
      tags: [docker]
    ```

---
<!-- MANUAL SECTIONS - DO NOT MODIFY THIS LINE -->
<!-- The sections below will be preserved during updates -->

## Business Logic & Implementation Decisions

<!-- Add project-specific business logic, unusual patterns, or architectural decisions -->
<!-- Example: Why certain algorithms were chosen, performance trade-offs, etc. -->

## Domain-Specific Context

<!-- Add domain terminology, internal services, external dependencies context -->
<!-- Example: Internal APIs, third-party services, business rules, etc. -->

## Special Cases & Edge Handling

<!-- Document unusual scenarios, edge cases, or exception handling patterns -->
<!-- Example: Legacy compatibility, migration considerations, etc. -->

## Additional Context

<!-- Add any other context that reviewers should know -->
<!-- Example: Security considerations, compliance requirements, etc. -->