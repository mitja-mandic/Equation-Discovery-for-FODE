# 5. Review, Decide, Repeat

Do not treat the Codex CLI report from `codex --yolo`, or the Claude Code CLI report from `claude --dangerously-skip-permissions`, as proof. Treat it as a claim.

First inspect the working tree:

```bash
git status
git diff --stat
git diff
```

Run or rerun the relevant tests yourself if the risk is high:

```bash
<test command>
```

Then ask the strategic model to audit the result:

```text
I used OAP. The execution agent completed this task.

Original work order:
<paste work order>

Agent final report:
<paste report>

Diff summary:
<paste git diff --stat>

Test output:
<paste relevant output>

Audit this as a reviewer and engineering manager:
- Did it satisfy the goal?
- Did it respect non-goals?
- Are the tests meaningful?
- Did the report overclaim?
- Are there security or architecture risks?
- Should I accept, repair, reject, or ask for another small PR?
```

The strategic audit should compress the evidence so the human can decide quickly. The human still owns the decision.

<Sidenote>
The key point of this step is not that the strategic model "approves" the agent. It is that the model helps compress where the evidence is, where the gaps are, and what decision the human actually has to make.
</Sidenote>

Use four outcomes:

**Accept.** The diff is small, tests are meaningful, docs are honest, and risks are acceptable.

**Repair.** The work is mostly right but needs a narrow fix. Create a second work order for Codex CLI with `codex --yolo`, or Claude Code CLI with `claude --dangerously-skip-permissions`.

**Reject.** The change violates the architecture, touches unrelated areas, fails tests, or solves the wrong problem. Abandon the branch or ask the agent to revert its own changes.

**Continue.** The task is good but incomplete by design. Ask the strategic model for the next PR-sized task.

<Sidenote>
`PR-sized` here means small enough that the resulting diff can still be understood and reviewed as one coherent change. If the outcome is too large to reason about, the work order was probably too broad.
</Sidenote>

End each loop with durable truth:

```bash
git status
git log --oneline -5
```

If the task is accepted:

```bash
git push -u origin oap-first-task
```

Open a pull request if that is part of your workflow. The agent must not merge its own PR. Release remains a human decision.
