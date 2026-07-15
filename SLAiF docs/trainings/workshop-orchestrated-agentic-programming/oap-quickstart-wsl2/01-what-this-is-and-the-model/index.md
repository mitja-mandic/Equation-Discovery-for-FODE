# What this is

This is a rapid-adoption guide for people who want to try **Orchestrated Agentic Programming** without reading the full manual first. It supports one setup only:

- Windows host.
- WSL2 Ubuntu execution environment.
- Git repository cloned inside the WSL2 Linux filesystem.
- High-autonomy execution with Codex CLI using `codex --yolo`.
- Equivalent high-autonomy execution with Claude Code CLI using `claude --dangerously-skip-permissions` or `claude --permission-mode bypassPermissions`.

This quickstart deliberately ignores other valid setups: Linux VMs, macOS VMs, containers, Windows Sandbox, persistent Windows VMs, cloud agents, and agent swarms. Those are useful later. The first run should be narrow.

The goal is simple: after reading this, a domain expert or project lead should be able to set up a bounded WSL2 workspace, ask a strategic model what should be built, create durable project instructions, delegate one small task to Codex CLI or Claude Code CLI, and review the result without becoming the agent's terminal assistant.

The method is not "trust the agent." The method is:

1. Put the execution agent in a bounded environment.
2. Use the strategic model for planning and audit.
3. Give the execution agent a small work order.
4. Require evidence.
5. Let the human decide.

# 1. The Model

OAP has three roles.

**The human is the manager.** The human owns the domain problem, priorities, risk, acceptance criteria, and release decision. The human may not be a professional software architect. That is fine. In OAP, the human supplies domain knowledge and judgment, then uses a strong strategic model to translate that into architecture, tools, and work orders.

**The strategic model is the control plane.** It helps answer questions such as:

- What kind of system is this really?
- Which stack is appropriate?
- What trust boundaries matter?
- What should not be built yet?
- What must the execution agent never improvise?
- Is the agent's report supported by evidence?

**The execution agent is disposable implementation labor.** In this quickstart the execution agent is either Codex CLI with `codex --yolo`, or Claude Code CLI with `claude --dangerously-skip-permissions` or `claude --permission-mode bypassPermissions`. It edits files, installs tools, runs tests, starts services, commits work, and writes a report.

The human should not type dependency commands for the agent all day. If the agent needs a test dependency, browser driver, package, local database, or compiler inside WSL2, the agent should usually install it itself and report what it did. The boundary is WSL2 plus Git, not constant human approval of every shell command.

The durable truth is not the chat and not the WSL2 machine. Durable truth is:

- the Git repository;
- `AGENTS.md` and `CLAUDE.md`;
- commits;
- pull requests;
- test output;
- documentation;
- review notes;
- release decisions.

The basic loop is:

```text
domain problem
  -> strategic discovery
  -> AGENTS.md / CLAUDE.md
  -> small work order
  -> Codex CLI / Claude Code CLI run
  -> evidence report
  -> strategic audit
  -> human decision
  -> next work order
```

Keep this loop short. One task should be small enough that the human can understand the diff and the evidence.
