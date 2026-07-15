# 4. Run The Agent

Before launching Codex CLI with `codex --yolo`, or Claude Code CLI with `claude --dangerously-skip-permissions`, create the repository instructions.

For Codex CLI, the durable instruction file is `AGENTS.md`. For Claude Code CLI, the durable instruction file is `CLAUDE.md`. For this quickstart, keep them equivalent. The simplest approach is to create both files with the same operational content:

```bash
cp AGENTS.md CLAUDE.md
git add AGENTS.md CLAUDE.md
git commit -m "Add OAP project constitution"
```

If the repository already has one of these files, do not overwrite it blindly. Ask the strategic model to merge the OAP constitution into the existing guidance.

<Sidenote>
This matters because `AGENTS.md` and `CLAUDE.md` are durable repository instructions, not just one-off chat prompts. If a rule is not written there, it is easy to lose in later runs.
</Sidenote>

Now create a branch:

```bash
git status
git switch -c oap-first-task
```

Then start one execution agent in the repository root.

Codex CLI:

```bash
codex --yolo
```

Claude Code CLI equivalent:

```bash
claude --dangerously-skip-permissions
```

Claude Code CLI equivalent setting form:

```bash
claude --permission-mode bypassPermissions
```

Paste a work order like this:

```text
Read AGENTS.md and CLAUDE.md first.

Current state:
- Repository: <name>
- Branch: oap-first-task
- Important existing files:
  - <files>

Goal:
- <one small feature, fix, test, or documentation improvement>

Acceptance criteria:
- <observable behavior>
- <tests or checks that must pass>
- <documentation that must be updated>

Non-goals:
- Do not change <unrelated area>.
- Do not add <unwanted dependency>.
- Do not modify production deployment.
- Do not touch secrets or real credentials.

Allowed local setup:
- You may install local development tools inside this WSL2 Ubuntu environment.
- Document every installed package or tool.
- Do not ask the human to run routine setup commands unless blocked by a real safety boundary.

Tests:
- Run <test command>.
- If tests cannot run, explain the exact environment blocker.
- Do not claim tests passed unless you ran them or CI proves it.

Workflow:
- Keep the diff small.
- Commit only related files.
- Do not merge.

Final report:
- Summary.
- Files changed.
- Commands run.
- Test results.
- Local tools installed.
- Risks and limitations.
- Suggested next task.
```

The execution agent should work inside WSL2. Let it inspect the repository, install missing local tools, run tests, and edit files. Do not micromanage every command. Interrupt only if it tries to cross a boundary: production credentials, host secrets, unrelated repositories, protected branches, or broad destructive actions.

<Sidenote>
If the human starts manually doing every other command instead of the agent, the OAP loop collapses quickly. The goal is not total oversight of each step, but good control over boundaries, scope, and evidence.
</Sidenote>

If the agent asks you to install a routine package, push back:

```text
You are running inside the approved WSL2 execution environment.
If this is ordinary local development setup, install it yourself,
document the command, and continue. Ask me only if the action crosses
a safety boundary.
```

That sentence is often enough to restore the OAP control loop.
