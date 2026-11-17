# Project instructions for Codex

## Role

Act as a practical Python development partner for this repository. Help design,
implement, debug, test, document, and review Python code. Use Git and the GitHub
CLI (`gh`) when repository or GitHub context is needed.

## Start of every task

1. Read this file and any more specific `AGENTS.md` files in the directories you
   will edit.
2. Inspect the repository before making assumptions:
   - `git status --short --branch`
   - relevant source and test files
   - `pyproject.toml`, lock files, CI workflows, and existing documentation
3. Follow the project's existing structure, Python version, dependency manager,
   formatter, linter, type checker, and test framework.
4. Preserve unrelated local changes. Never overwrite or discard work that was
   already present.

## Python development

- Prefer clear, maintainable Python over clever or overly abstract code.
- Keep functions and modules focused, and use descriptive names.
- Add type hints to new or changed public functions unless the surrounding code
  deliberately does not use them.
- Use `pathlib` for filesystem paths and context managers for resources.
- Handle expected failure modes explicitly. Do not silently catch broad
  exceptions.
- Add docstrings where behavior, parameters, return values, or side effects are
  not obvious.
- Do not add a dependency when the standard library or an existing dependency is
  sufficient.
- Do not change public APIs, file formats, or command-line behavior without
  calling out the compatibility impact.
- Never hard-code credentials, tokens, private URLs, or machine-specific paths.
  Use environment variables and provide an `.env.example` when configuration
  needs documenting. Never commit a real `.env` file.

## Configuration style

- Do not introduce environment variables for ordinary user-editable settings unless I explicitly request them.
- Put mode switches, file paths, model options, and similar settings in a clearly labeled configuration section in the source code.
- Prefer simple, explicit constants such as `DATA_MODE = "spectrum"`.
- When editing existing code, remove unnecessary configuration indirection instead of preserving it.
- Optimize for code that is obvious to someone running the script directly.

## Testing and quality checks

- Add or update tests for behavior changes and bug fixes.
- First run the smallest relevant test set, then the broader suite when practical.
- Use the commands already defined by the project. If none are defined, prefer:
  - tests: `python -m pytest`
  - linting: `ruff check .`
  - formatting check: `ruff format --check .`
  - type checking: `mypy .`
- Do not introduce a new quality tool only to complete a small task.
- If a check cannot run, state exactly why and report what was verified instead.

## Git workflow

- Review `git status` and `git diff` before and after editing.
- Keep changes focused on the requested task; avoid opportunistic rewrites.
- Do not use destructive commands such as `git reset --hard`, force-push, or
  deleting branches unless the user explicitly requests the exact operation.
- Do not amend commits, rebase shared branches, create commits, or push changes
  unless requested.
- When asked to create a branch, use a short descriptive name such as
  `feat/add-parser` or `fix/config-loading`.
- When asked to commit, use an imperative, concise message that explains the
  purpose of the change.

## GitHub CLI (`gh`)

- Prefer `gh` over manually calling the GitHub REST API.
- Before relying on GitHub access, check authentication and repository context:

  ```bash
  gh auth status
  gh repo view --json nameWithOwner,url,defaultBranchRef
  ```

- If authentication is missing, stop the GitHub-dependent step and tell the user
  to run `gh auth login`. Never request, print, or store their token.
- Read-only GitHub commands are allowed when useful, for example:

  ```bash
  gh issue view <number> --comments
  gh pr view <number> --comments
  gh pr diff <number>
  gh pr checks <number>
  ```

- Treat remote mutations as explicit actions. Only create or edit issues, create
  pull requests, push branches, merge, release, or change repository settings
  when the user's request authorizes that action.
- Before opening a pull request, verify tests, inspect the final diff, and prepare
  a concise title and body covering the problem, solution, and verification.
- Never merge a pull request or bypass failing checks unless explicitly asked.

## Working style

- For a small change, proceed directly. For a larger or ambiguous change, briefly
  state the intended approach and clarify only decisions that materially affect
  the result.
- Diagnose the root cause before changing code.
- Prefer focused patches that are easy to review.
- Update README or usage documentation when setup, configuration, or user-facing
  behavior changes.
- Comment code to explain non-obvious reasoning, not to narrate straightforward
  syntax.

## Completion report

At the end of a task, summarize:

1. what changed;
2. which checks or tests passed;
3. any remaining limitations or user action required;
4. GitHub actions performed, if any, with relevant branch, issue, or pull-request
   references.
