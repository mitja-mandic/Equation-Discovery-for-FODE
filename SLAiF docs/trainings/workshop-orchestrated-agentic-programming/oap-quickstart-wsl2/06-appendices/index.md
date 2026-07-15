# Appendix A: Preflight Checklist

Use this before any Codex CLI `codex --yolo` run or Claude Code CLI `claude --dangerously-skip-permissions` run.

```text
[ ] I am inside WSL2 Ubuntu, not a normal Windows shell.
[ ] The repository is under ~/work or another Linux filesystem path.
[ ] The Git remote is configured.
[ ] The working tree is clean or intentionally dirty.
[ ] AGENTS.md exists for Codex CLI.
[ ] CLAUDE.md exists for Claude Code CLI.
[ ] No production .env file is present.
[ ] No host/prod SSH private keys were copied into WSL2.
[ ] Guest-local ~/.ssh is expected and contains only scoped access material.
[ ] No cloud, kube, Docker, browser, or password-manager secrets are present unless explicitly scoped.
[ ] The first task is PR-sized.
[ ] The work order has goal, acceptance criteria, non-goals, tests, and report requirements.
[ ] I know how to abandon this branch.
[ ] The execution agent cannot merge its own PR.
```

# Appendix B: Copy-Paste Prompts

## Strategic discovery prompt

```text
I am starting an OAP project.

Domain problem:
<problem>

Users:
<users>

Constraints:
<security, privacy, cost, deployment, operations>

Please tell me:
1. What kind of system this really is.
2. Which architecture and stack fit.
3. What trust boundaries matter.
4. What should be excluded from the first slice.
5. What tests should prove the first useful behavior.
6. What rules belong in AGENTS.md and CLAUDE.md.
7. The first PR-sized execution task.
```

## Execution work-order prompt

```text
Read AGENTS.md and CLAUDE.md first.

Current state:
<state>

Goal:
<one small task>

Acceptance criteria:
<criteria>

Non-goals:
<explicit exclusions>

Allowed local setup:
You may install required local development tools inside this WSL2 Ubuntu
environment. Document what you install. Do not ask me to run routine setup
commands unless blocked by a real safety boundary.

Tests:
<commands>

Workflow:
Keep the diff small. Commit only related files. Do not merge.

Report:
Summary, files changed, commands run, test results, installed tools,
risks, and suggested next task.
```

## Repair prompt

```text
This is a repair task.

Original goal:
<goal>

Problem found in review:
<problem>

Repair only this issue:
<narrow repair>

Do not refactor unrelated code.
Do not broaden scope.
Run the relevant tests and report exact results.
```

## Strategic audit prompt

```text
Audit this OAP execution result.

Work order:
<paste>

Agent report:
<paste>

Diff summary:
<paste>

Test output:
<paste>

Tell me:
1. Whether the goal was satisfied.
2. Whether non-goals were respected.
3. Whether tests are meaningful.
4. Whether the report overclaims.
5. Whether risks remain.
6. Whether to accept, repair, reject, or continue.
```

# Appendix C: Minimal Project Constitution

Create both `AGENTS.md` and `CLAUDE.md` from this template. Keep them short enough that an agent will actually follow them.

```markdown
# Project Instructions

## Mission
This repository implements <product>. Preserve <core promise>.

## Discovery Summary
- Domain problem:
- Product shape:
- Chosen architecture:
- Stack/tool rationale:
- First release scope:
- Explicit non-goals:

## Architecture
- Main components:
- Data flow:
- Trust boundaries:
- External services:

## Non-negotiable Rules
- Never commit secrets.
- Never log raw credentials.
- Do not access production systems.
- Do not merge your own PR.
- Keep changes PR-sized.

## Workflow
- Start from current main.
- Create a feature branch.
- Commit only related files.
- Keep the final report factual.

## Local Setup
- Install missing local development tools only inside the approved WSL2 Ubuntu environment.
- Document installed packages and setup commands.
- Do not ask the human to perform routine setup unless blocked by a real safety boundary.

## Tests
- Required unit tests:
- Required integration tests:
- Required lint/type checks:
- If a test cannot run, report the exact blocker.

## Documentation
- Update docs when behavior changes.
- Do not claim release readiness without human approval.

## Final Report
- Branch:
- Commit:
- Summary:
- Files changed:
- Commands run:
- Test results:
- Local tools installed:
- Risks:
- Suggested next task:
```

# Appendix D: Source Notes

This quickstart is distilled from `final/orchestrated-agentic-programming-v1.0.1-2026-06-14.md`.

Tool-specific claims were checked against current public documentation on 2026-06-14:

- OpenAI Codex CLI documents `--dangerously-bypass-approvals-and-sandbox, --yolo` as running without approvals or sandboxing and says to use it only inside an externally hardened environment: [Codex CLI reference](https://developers.openai.com/codex/cli/reference)
- OpenAI Codex documents `AGENTS.md` as custom project instructions: [AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md)
- Anthropic Claude Code CLI documents `--dangerously-skip-permissions` as skipping permission prompts and equivalent to `--permission-mode bypassPermissions`: [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)
- Anthropic documents `CLAUDE.md` as persistent project/user instructions for Claude Code: [Claude Code memory documentation](https://code.claude.com/docs/en/memory)
- Microsoft WSL installation and configuration references: [WSL install](https://learn.microsoft.com/en-us/windows/wsl/install), [WSL filesystems](https://learn.microsoft.com/en-us/windows/wsl/filesystems), [WSL configuration](https://learn.microsoft.com/en-us/windows/wsl/wsl-config)

# Acknowledgement

We acknowledge the support of the EC/EuroHPC JU and the Slovenian Ministry of HESI via the project SLAIF (grant number 101254461).
