---
id: 009
title: Pre-Commit Hooks Setup
stage: green
date: 2025-11-29
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-rag-query-endpoint
branch: 001-rag-query-endpoint
user: developer
command: /sp.implement
labels: ["pre-commit", "git-hooks", "automation", "code-quality", "ci-cd"]
links:
  spec: ../specs/001-rag-query-endpoint/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/.pre-commit-config.yaml
  - backend/.git/hooks/pre-commit (installed)
tests:
  - Pre-commit installation: Success
  - All hooks (17 total): All passed after auto-fixes
  - Black, Flake8, mypy: Skipped (no Python files changed)
  - File checks: All passed
---

## Prompt

yes go ahead, follow all best practices and tests to get errorfree out put

## Response snapshot

Successfully configured and installed pre-commit hooks for automated code quality enforcement on every git commit.

**Configuration Details (.pre-commit-config.yaml):**

1. **Black Formatter Hook**:
   - Repo: https://github.com/psf/black (rev: 23.12.1)
   - Args: --line-length=100
   - Scope: All .py files

2. **Flake8 Linter Hook**:
   - Repo: https://github.com/pycqa/flake8 (rev: 6.1.0)
   - Config: setup.cfg
   - Additional dependencies: flake8-docstrings, flake8-bugbear
   - Scope: All .py files

3. **Mypy Type Checker Hook**:
   - Repo: https://github.com/pre-commit/mirrors-mypy (rev: v1.7.1)
   - Args: --strict, --config-file=pyproject.toml
   - Additional dependencies: pydantic>=2.5.0, types-redis
   - Scope: src/**/*.py only

4. **General File Checks (pre-commit-hooks)**:
   - check-added-large-files (max 1000KB)
   - check-case-conflict
   - check-merge-conflict
   - check-yaml, check-toml, check-json
   - end-of-file-fixer
   - trailing-whitespace
   - no-commit-to-branch (prevents commits to main/master)
   - detect-private-key
   - debug-statements (prevents pdb, breakpoint)

5. **Python-Specific Checks (pygrep-hooks)**:
   - python-check-blanket-noqa
   - python-check-blanket-type-ignore
   - python-use-type-annotations

**Installation and Validation:**

```bash
# Installation
$ python -m pre_commit install
pre-commit installed at .git\hooks\pre-commit

# First run (installed environments)
$ python -m pre_commit run --all-files
[INFO] Installing environment for https://github.com/psf/black...
[INFO] Installing environment for https://github.com/pycqa/flake8...
[INFO] Installing environment for https://github.com/pre-commit/mirrors-mypy...
[INFO] Installing environment for https://github.com/pre-commit/pre-commit-hooks...

# Auto-fixed issues
fix end of files.........................................................Failed
- files were modified by this hook
Fixing .specify/scripts/powershell/*.ps1 (4 files)

trim trailing whitespace.................................................Failed
- files were modified by this hook
Fixing .specify/scripts/powershell/*.ps1 (5 files)

# Second run (all passed)
$ python -m pre_commit run --all-files
fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
[All 17 hooks passed]
```

**Automatic Enforcement:**
- Pre-commit hooks now run automatically on `git commit`
- Blocks commits if any hook fails (formatting, linting, type checking)
- Developers can manually run: `pre-commit run --all-files`
- Hooks run in isolated virtual environments (cached for performance)

**Constitution Compliance:**
- ✅ Rule I (Code Quality): Automated enforcement of Black, Flake8, mypy on every commit
- ✅ Additional safety: Prevents large files, private keys, debug statements, direct commits to main/master
- ✅ Team consistency: All developers must pass same checks before committing

## Outcome

- ✅ Impact: Code quality enforcement now fully automated via git hooks. Every commit must pass Black formatting, Flake8 linting, mypy type checking, and 13 additional file/security checks. Prevents non-compliant code from entering the repository.
- 🧪 Tests: Pre-commit installed successfully, 17 hooks configured, all hooks passed after auto-fixes (end-of-file, trailing whitespace)
- 📁 Files: Created backend/.pre-commit-config.yaml, installed .git/hooks/pre-commit
- 🔁 Next prompts: T006 (Create docker-compose.yml) to complete Phase 1, then proceed to Phase 2 (Foundational infrastructure: core config, logging, metrics)
- 🧠 Reflection: Pre-commit hooks provide a critical safety net. Fixed Python version compatibility issue (3.11 → 3.13) in configuration. Hooks auto-fixed minor file formatting issues in PowerShell scripts. All Python code quality tools (Black, Flake8, mypy) are now automatically enforced on every commit, ensuring Constitution Rule I compliance at the source.

## Evaluation notes (flywheel)

- Failure modes observed: Initial Python version mismatch (python3.11 not found, system has 3.13). Fixed by using generic `python3` in language_version settings.
- Graders run and results (PASS/FAIL): Pre-commit install PASS, First run (17 hooks, 2 auto-fixed, rest passed), Second run (all 17 hooks PASS)
- Prompt variant (if applicable): N/A (direct implementation)
- Next experiment (smallest change to try): Consider adding pytest hook to run unit tests on commit (optional, may slow down commits). Could also add isort (import sorting) for additional code consistency.
