# Datum DBT Tool - Complete Specification & Architecture

## Executive Summary

**Product:** A user-friendly CLI tool that helps users schedule dbt projects on their local infrastructure with datum cloud as an optional UI/reporting layer.

**Goal:** Make scheduling dbt easy for local environments (Ubuntu/Linux), with extensibility to K8s later. Ship v1 tool first, cloud infrastructure second.

**Distribution:** Publish to PyPI as `datum-cli`. Users install via `pip install datum-cli` and run as `datum` command globally.

---

## Core Philosophy

- **Tool-first approach:** Build the CLI as a complete, self-contained product. Cloud is optional reporting layer.
- **Minimal dependencies:** Use stdlib wherever possible, add only battle-tested packages.
- **Shipping speed:** v1 is feature-complete for local scheduling, not perfect for all edge cases.
- **Debugging-friendly:** Every action logs, every failure is debuggable, validation prevents mistakes.
- **Pythonic code:** Follow PEP 20, use modern Python 3.13+ typing, Pydantic v2 for validation.

---

## v1 Feature Set

### Core Commands

#### `datum dbt init --repo-path <path>`
- Initialize a new dbt project for datum
- **Actions:**
  - Validate dbt_project.yml exists
  - Generate SSH key: `~/.datum/keys/{project-id}.pem` (600 permissions)
  - Generate public key: `~/.datum/keys/{project-id}.pub`
  - Create `~/.datum/config.yaml` with project config
  - Validate profiles.yml location (auto-detect ~/.dbt/profiles.yml or prompt)
  - Show next steps clearly
- **Output:** Confirmation of all setup steps, instructions to share public key to datum cloud (later)

#### `datum dbt validate`
- Pre-flight check before scheduling
- **Checks:**
  - dbt_project.yml exists and valid
  - profiles.yml exists and readable
  - SSH key exists with correct permissions (600)
  - dbt target exists in profiles.yml
  - dbt command runs without errors (test connection)
- **Auto-repair mode:** Detect common issues (wrong permissions, missing files) and offer fixes
- **Output:** ✓ / ✗ status for each check, suggestions for fixes

#### `datum dbt run [--target <target>] [--profile <path>] [--dry-run]`
- Execute dbt locally with full logging
- **Actions:**
  - Load config from ~/.datum/config.yaml
  - Validate prerequisites (same as `validate`)
  - Execute: `dbt run --target <target> --profiles-dir <profiles-dir>`
  - Stream output to terminal in real-time with timestamps
  - Capture all stdout/stderr
  - Save run record with metadata
- **Options:**
  - `--dry-run`: Show what would run without executing
  - `--vars '{"key": "value"}'`: Pass dbt vars
  - `--timeout 3600`: Kill job after N seconds
- **Output:** Real-time streaming + success/failure summary

#### `datum dbt schedule --cron "<cron-expression>" [--target <target>]`
- Add a cron job to execute dbt on schedule
- **Actions:**
  - Validate cron expression syntax
  - Validate project prerequisites
  - Show what will be added to crontab (dry-run first)
  - Add entry to user's crontab: `0 10 * * * /usr/bin/datum-dbt-run {project-id} 2>&1`
  - Store schedule config in ~/.datum/config.yaml
- **Crontab entry behavior:**
  - Calls internal command: `datum dbt run --project {project-id}`
  - Pipes output to logging handler
  - Runs with user's environment (not root)
- **Output:** Confirmation + next steps (validate, check logs)

#### `datum dbt schedule --webhook [--port 8080]`
- Start webhook server for external triggers (Airflow, Dagster)
- **Actions:**
  - Start FastAPI server on `0.0.0.0:{port}`
  - Listen for POST requests
  - Endpoint: `POST /trigger/{project_id}/{run_id}`
  - Optional payload: `{"target": "prod", "vars": {...}, "timeout": 3600}`
  - Validate request, execute dbt run, return status
  - Webhook runs in background (daemonize or use systemd)
- **Output:** "Webhook listening on http://localhost:8080/trigger/{project-id}/run-{id}"
- **Response format:**
  ```json
  {
    "run_id": "abc123",
    "status": "running|queued|error",
    "output_url": "file:///home/user/.datum/runs/abc123/run.json"
  }
  ```

#### `datum dbt schedule --status`
- Show current schedule configuration
- **Output:**
  - Project name + status (ACTIVE/INACTIVE)
  - All schedules (cron + webhook)
  - Last run time + status
  - Next scheduled run time
  - Crontab location + entry

#### `datum dbt logs [--last 10] [--status SUCCESS|FAILED|TIMEOUT] [--follow]`
- View execution history and logs
- **Actions:**
  - Read all run records from ~/.datum/runs/
  - Display in table format (Run ID, Time, Status, Duration, Exit Code)
  - Allow filtering by status
- **Output:** Table of recent runs

#### `datum dbt logs <run-id> [--raw]`
- View full log for a specific run
- **Output:**
  - Metadata: timestamp, duration, exit code, command
  - Formatted output (with timestamps) or raw output
  - Path to full log files
  - Suggestion based on error (e.g., "Database connection failed → check profiles.yml credentials")

#### `datum dbt config [--project-path] [--profiles-path] [--target]`
- Update configuration after init
- **Actions:**
  - Interactively or via flags update ~/.datum/config.yaml
  - Validate changes before saving
  - Show current config
- **Output:** Confirmation of changes

---

## Data Models (Pydantic v2)

```python
# All models in src/datum/core/config.py

DbtProjectConfig:
  - project_id: str (auto-generated UUID)
  - project_path: Path (validated, must have dbt_project.yml)
  - profiles_path: Path (default ~/.dbt/profiles.yml)
  - target: str (default "dev")
  - dbt_version: str (auto-detected)

ScheduleConfig:
  - cron_expression: str (validated by croniter)
  - enabled: bool (default True)
  - created_at: datetime
  - last_run_at: Optional[datetime]
  - next_run_at: Optional[datetime]

WebhookConfig:
  - enabled: bool (default False)
  - port: int (1024-65535)
  - host: str (default "0.0.0.0")
  - token: Optional[str] (for future auth)

RunRecord:
  - run_id: str (UUID)
  - project_id: str
  - timestamp: datetime
  - command: str (what was executed)
  - exit_code: int
  - duration_seconds: float
  - status: str ("SUCCESS" | "FAILED" | "TIMEOUT")
  - stdout: str
  - stderr: str

DatumConfig (root, ~/.datum/config.yaml):
  - version: str ("1.0")
  - project: DbtProjectConfig
  - schedule: Optional[ScheduleConfig]
  - webhook: Optional[WebhookConfig]
  - private_key_path: Path
  - runs_dir: Path (default ~/.datum/runs/)
```

---

## File Structure

```
datum-dbt/
├── src/datum/
│   ├── __init__.py
│   ├── __main__.py                 # Entry point for `python -m datum`
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py                 # Typer app, command routing
│   │   └── commands/
│   │       ├── __init__.py
│   │       ├── init.py             # datum dbt init
│   │       ├── auth.py             # datum dbt auth validate (future)
│   │       ├── config.py           # datum dbt config
│   │       ├── validate.py         # datum dbt validate
│   │       ├── run.py              # datum dbt run
│   │       ├── schedule.py         # datum dbt schedule (cron + webhook)
│   │       └── logs.py             # datum dbt logs
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py               # Pydantic models + file I/O
│   │   ├── auth.py                 # SSH key generation
│   │   ├── executor.py             # dbt execution + logging
│   │   ├── scheduler.py            # Cron job management
│   │   ├── webhook.py              # FastAPI webhook server
│   │   ├── storage.py              # Run storage/retrieval
│   │   ├── validators.py           # Pre-flight checks + auto-repair
│   │   └── utils.py                # Helpers (ID generation, etc)
│   └── errors.py                   # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_auth.py
│   ├── test_executor.py
│   ├── test_scheduler.py
│   ├── test_webhook.py
│   └── test_cli.py
├── pyproject.toml                  # Project metadata + dependencies
├── README.md                        # User guide
├── LICENSE
└── .gitignore
```

---

## Dependencies (pyproject.toml)

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "datum"
version = "0.1.0"
description = "Schedule dbt projects locally with datum cloud reporting"
readme = "README.md"
license = {text = "MIT"}
authors = [{name = "Datum Labs", email = "contact@datumlabs.io"}]
requires-python = ">=3.11"
keywords = ["dbt", "scheduling", "data", "analytics", "workflow"]

dependencies = [
    "typer[all]>=0.9,<1.0",           # CLI framework
    "pydantic>=2.0,<3.0",             # Data validation
    "pydantic-settings>=2.0,<3.0",    # Config from YAML/env
    "pyyaml>=6.0,<7.0",               # YAML parsing
    "python-crontab>=3.0,<4.0",       # Cron management
    "croniter>=2.0,<3.0",             # Cron parsing/validation
    "fastapi>=0.104,<1.0",            # Webhook server
    "uvicorn>=0.24,<1.0",             # ASGI server
    "cryptography>=41.0,<43.0",       # SSH key generation
    "rich>=13.0,<14.0",               # Terminal formatting
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4,<8.0",
    "pytest-cov>=4.1,<5.0",
    "ruff>=0.1,<1.0",
    "mypy>=1.6,<2.0",
    "black>=23.0,<24.0",
]

[project.scripts]
datum = "datum.cli.main:app"

[tool.hatch.build.targets.wheel]
packages = ["src/datum"]
```

---

## Key Implementation Details

### 1. SSH Key Generation (Secure)
- Generate 2048-bit RSA key pair in `~/.datum/keys/{project-id}.pem`
- Set permissions to 600 (readable only by user)
- Store public key as `{project-id}.pub`
- Never ask user to generate keys manually

### 2. Config File Handling
- Location: `~/.datum/config.yaml`
- Always load with validation (Pydantic)
- Auto-migrate config if version changes
- Handle missing/corrupted files gracefully with clear error messages

### 3. Run Execution & Logging
- Each run gets unique ID: `{project-id}-{timestamp}-{uuid[:8]}`
- Create directory: `~/.datum/runs/{run_id}/`
- Save files:
  - `metadata.json` (structured data)
  - `output.log` (stdout + stderr combined, timestamped)
  - `stdout.log` (stdout only)
  - `stderr.log` (stderr only)
- Stream output to terminal in real-time with `[HH:MM:SS]` timestamps
- Capture exit code + duration

### 4. Cron Integration
- Use `python-crontab` library (safer than shell scripts)
- Crontab entry format: `0 10 * * * /usr/local/bin/datum dbt run --project {project-id} 2>&1`
- Always show user what will be added before modifying crontab
- Allow user to review/edit crontab manually after
- Store schedule info in config for `--status` command

### 5. Webhook Server
- FastAPI app with single endpoint: `POST /trigger/{project_id}/{run_id}`
- Request validation (basic auth can be v2)
- Response includes run_id, status, output location
- Run webhook as background process (systemd unit template for later)
- For v1: user must manually start daemon or use screen/tmux

### 6. Validation & Auto-Repair
- Pre-flight checks before any command:
  - dbt_project.yml exists + valid YAML
  - profiles.yml exists + accessible
  - SSH key exists with 600 permissions
  - dbt target exists in profiles.yml
  - Can connect to database (run `dbt debug`)
- Offer automated fixes for:
  - Permissions: `chmod 600 {key}`
  - Missing files: Show path + how to create
  - Profile issues: Show profiles.yml location
- `datum dbt validate` lists all issues + fixes
- `--auto-fix` flag applies fixes (with confirmation)

### 7. Debugging Experience
- Every command shows what it's doing (✓/✗ indicators)
- Errors include suggestions (not just "failed")
- `datum dbt logs` shows last 10 runs in table
- `datum dbt logs {run-id}` shows full formatted log with timestamps
- Log files are stored locally (easy to grep, inspect, parse)
- Clear indication of where logs are stored

---

## PyPI Publishing Setup

### Before Publishing
1. Create account on pypi.org (or testpypi.org for testing)
2. Generate API token: pypi.org → Account Settings → API tokens
3. Add token to `~/.pypirc` or use GitHub Actions secret

### Publishing Command
```bash
# Build
python -m build

# Upload to TestPyPI (test first)
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

### Package Naming & Metadata
- Package name: `datum`
- Import name: `datum`
- Console script: `datum` (global command)
- Keywords: "dbt", "scheduling", "data", "analytics"
- Homepage: https://datumlabs.io (or GitHub)
- Repository: https://github.com/datumlabs/datum-dbt
- License: MIT

### Post-Publishing
- Update PyPI page with README (auto from README.md)
- Add badges (build status, PyPI version, downloads)
- Set up GitHub releases to auto-publish on tags

---

## Development Instructions for Agent

### Phase 1: Foundation (2-3 hours)
1. **Project setup**
   - Create pyproject.toml with all dependencies
   - Set up directory structure
   - Create __init__.py files with version
   - Add .gitignore for Python

2. **Config system (Pydantic models)**
   - Write all dataclasses in config.py
   - Implement config file I/O (load/save ~/.datum/config.yaml)
   - Add validation for all fields
   - Handle missing/invalid configs gracefully

3. **Auth system**
   - SSH key generation in auth.py
   - Public key extraction
   - Permission handling (chmod 600)
   - Key validation

### Phase 2: CLI Skeleton (1 hour)
1. **Main app (typer)**
   - Create main.py with Typer app
   - Add command routing (init, run, schedule, logs, validate, config)
   - Add global options (--debug, --project)
   - Set up logging

2. **Placeholder commands**
   - Create each command file with docstring + typer.echo("TODO")
   - All imports correct but functions empty

### Phase 3: Core Features (4-5 hours)
1. **Executor** (run.py)
   - Run dbt subprocess with real-time streaming
   - Capture stdout/stderr
   - Handle timeouts + errors
   - Save run record

2. **Storage** (storage.py)
   - Save/load run records
   - Query runs by ID, timestamp, status
   - Clean up old runs (optional, v2)

3. **Validators** (validators.py)
   - Pre-flight checks (all 5 checks listed above)
   - Auto-repair suggestions
   - Clear error messages with fixes

4. **Scheduler** (scheduler.py)
   - Validate cron expressions
   - Add/remove crontab entries
   - Show crontab status

### Phase 4: CLI Commands (3-4 hours)
1. **init.py** - Full implementation with user prompts
2. **run.py** - Execute dbt with logging
3. **schedule.py** - Cron + webhook logic
4. **logs.py** - Display run history + details
5. **validate.py** - Pre-flight checks
6. **config.py** - Update configuration

### Phase 5: Webhook Server (2 hours)
1. **webhook.py**
   - FastAPI app with POST /trigger/{project_id}/{run_id}
   - Request validation
   - Execute dbt run in background
   - Return status response

2. **Integration**
   - Add `datum dbt schedule --webhook` command
   - Start server as subprocess or daemon
   - Show webhook URL to user

### Phase 6: Testing & Polish (2 hours)
1. **Unit tests** (tests/*.py)
   - Config loading/saving
   - Cron validation
   - Executor (mock dbt calls)
   - Storage (create/read runs)

2. **Integration tests**
   - Full CLI flow (init → run → logs)
   - Error handling (missing files, bad config)

3. **Edge cases**
   - Windows paths (defer for v2, document as Linux-only)
   - Permission errors
   - Crontab doesn't exist (create it)
   - Concurrent runs (same project, different run IDs)

---

## Testing Strategy

### Unit Tests
- Config models (validation, serialization)
- Auth (key generation, permissions)
- Validator (issue detection)
- Storage (save/load runs)

### Integration Tests
- Full command flow: `init` → `validate` → `run` → `logs`
- Error scenarios: missing files, bad cron, profile issues
- Dry-run modes

### Manual Testing Checklist
- [ ] `datum dbt init --repo-path ./` creates config + key
- [ ] `datum dbt validate` passes with valid project
- [ ] `datum dbt run` executes dbt + saves logs
- [ ] `datum dbt logs` shows recent runs
- [ ] `datum dbt schedule --cron "0 10 * * *"` adds crontab entry
- [ ] `datum dbt schedule --status` shows cron info
- [ ] Invalid cron rejected with helpful error
- [ ] Logs are saved to ~/.datum/runs/{run_id}/

---

## Error Handling

Every command should:
1. Catch exceptions early
2. Provide context (what were we doing?)
3. Suggest a fix (what should user do?)
4. Log full traceback to file (for debugging)
5. Exit with code 0 (success) or 1 (failure)

### Common Errors to Handle
- Missing dbt_project.yml → "No dbt project found at {path}. Initialize with: datum dbt init"
- Bad SSH key permissions → "SSH key too open. Fix: chmod 600 {key}"
- Database connection failed → "Could not connect to database. Check profiles.yml: {error}"
- Cron syntax invalid → "Invalid cron expression. Example: '0 10 * * *' (daily at 10 AM)"
- Permission denied → "Cannot write to {path}. Check file permissions."

---

## Documentation for Users

### README.md Structure
1. **Installation** - `pip install datum-cli`
2. **Quick Start** - 5 min walkthrough
3. **Commands Reference** - All commands with examples
4. **Configuration** - ~/.datum/config.yaml explained
5. **Debugging** - How to view logs, common issues
6. **Future Roadmap** - K8s, cloud sync, etc

### Example Usage Flow
```bash
# Install
pip install datum-cli

# Initialize
cd my-dbt-project
datum dbt init --repo-path .

# Validate setup
datum dbt validate

# Test run locally
datum dbt run

# Schedule daily at 10 AM
datum dbt schedule --cron "0 10 * * *"

# Check logs
datum dbt logs --last 5
datum dbt logs abc123
```

---

## Future Roadmap (v2+)

- [ ] Cloud sync (push run results to datum cloud UI)
- [ ] K8s job support (`--executor kubernetes`)
- [ ] Dagster/Airflow plugins
- [ ] Web UI for local runs
- [ ] Advanced scheduling (retries, backoff, alerts)
- [ ] Multiple projects in one config
- [ ] Environment variable templating in config
- [ ] Webhook authentication (API keys)
- [ ] Windows support
- [ ] Docker containerization

---

## Success Criteria for v1

✅ User can install via PyPI  
✅ User can init, validate, run, schedule with single config file  
✅ All runs are logged locally with searchable history  
✅ Webhook works for basic external triggers  
✅ Clear error messages for 95% of failure cases  
✅ No cloud infrastructure required (cloud is optional)  
✅ Cron jobs run reliably  
✅ Debugging is straightforward (logs are easy to find/read)  

---

## Build Order Recommendation

1. **Config + Auth** → Foundation everything depends on
2. **Executor + Storage** → Core functionality
3. **Validators** → Quality + UX
4. **CLI Commands** → User interface
5. **Scheduler** → Scheduling logic
6. **Webhook** → External triggers
7. **Tests + Docs** → Ship-ready

**Estimated total time: 12-16 hours of focused coding**

---

## Code Quality Standards

- All code typed with Python 3.13+ type hints
- Pydantic v2 for all data models
- Docstrings for all functions (Google style)
- No magic numbers (use named constants)
- Errors are informative (context + suggestion)
- Tests should cover happy path + 3 error scenarios per feature
- Use `rich` for beautiful terminal output (colors, tables, progress)
- Follow Black formatter (line length 100)
- Use Ruff for linting

---

## Ready to Code

Agent should now have everything needed to:
1. Build the project structure
2. Implement each feature with clear scope
3. Write tests as they go
4. Prepare for PyPI publishing

**All architectural decisions are finalized. Focus on shipping clean, tested, user-friendly code.**
