# Part IV: Coding and Verification

## IV.1 The Execution Layer

The execution layer is the coding agent operating against a repository. It is valuable because it can perform implementation labor: navigating files, editing code, installing tools, running test commands, interpreting failures, and iterating. It is not valuable because it remembers the whole project forever. Continuity belongs to the strategic layer and the repository.

### What the executor should own

The executor should own:

- mechanical implementation;
- local exploration;
- local dependency and tool setup inside the execution VM;
- disposable service setup for tests;
- creating or updating tests;
- running specified verification;
- fixing failures within scope;
- documenting changed behavior;
- producing commits and PRs;
- reporting exact outcomes.

The executor should not own:

- product strategy;
- release claims;
- security exceptions;
- production access decisions;
- broad scope expansion;
- final merge decisions.
- long-term project memory;
- assigning routine environment chores to the human.

### The executor as constrained implementer

A coding agent is most useful when the task is narrow enough that success can be evaluated. "Improve the system" is too vague. "Add a fail-closed check for unknown pricing and tests proving no provider call occurs before rejection" is better.

The executor should not need to infer the release roadmap. It should not need to decide whether a feature belongs in RC2. It should receive a bounded task and return evidence. If it needs a tool to complete that task, it should install or configure it within the allowed execution boundary and report the change.

### One task, one context

The execution agent's context should be treated as a consumable work buffer. It should last long enough to complete the current PR-sized task and no longer. Between tasks, the agent can be compacted, reset, or given a fresh work order from the strategic model.

This prevents two common failures:

- the executor accumulates stale assumptions from earlier work;
- the human tries to preserve context by manually narrating every detail to the executor.

The strategic model carries continuity. The executor carries action. The repository carries truth.

### Required executor report

Every execution task should end with a report like:

```markdown
## Agent Report

Branch: feature/short-name
Commit: abc1234
Pull request: https://github.com/org/repo/pull/123

## Summary
- ...

## Files changed
- ...

## Tests run
- command: result
- command: result

## Documentation impact
- ...

## Safety confirmations
- No production secrets committed.
- No unrelated files changed.
- No skipped test reported as passed.
- New local tools or dependencies installed only inside allowed execution space.

## Known limitations
- ...

## Follow-up recommended
- ...
```

This report is not proof by itself. It is an index into evidence that the strategic model can inspect and the human can interrogate.

### Executor discipline

Execution agents should:

- start from the correct branch;
- inspect before editing;
- make small commits;
- use existing project patterns;
- avoid broad refactors unless requested;
- run focused tests first, broader tests when needed;
- install permitted dependencies without pulling the human into routine setup;
- stop and report real blockers;
- never fake a PR URL;
- never claim unavailable CI results.

The most dangerous executor is not the one that fails. It is the one that succeeds loudly while quietly violating scope.

## IV.2 PR-Sized Delegation

OAP's atomic unit is the pull request. A PR is small enough for the strategic model to inspect deeply, large enough to preserve useful implementation context, and structured enough to carry evidence. The human does not need to read every line by default, but the PR must be coherent enough that the human can demand precise answers about it.

<ExpandingSideImg
  src="../assets/fig-04-pr-pipeline.svg"
  alt="PR-sized delegation pipeline."
  caption="PR-sized delegation pipeline."
/>

### Why PR-sized work works

PR-sized delegation has several advantages:

- It forces scope.
- It creates a durable diff.
- It supports CI.
- It invites strategic review and human interrogation.
- It can be reverted.
- It preserves history.
- It separates implementation from merge authority.

This is why "one prompt, one PR" is often a good default. There are exceptions: investigation-only tasks, verification-only runs, or documentation planning may not need PRs. But implementation work should normally produce a reviewable branch that the strategic model can summarize, challenge, and connect to tests.

### Anatomy of a PR-sized task

A good task has:

- a name;
- a reason;
- a defined scope;
- explicit non-goals;
- relevant files;
- acceptance criteria;
- tests;
- documentation impact;
- report requirements;
- permitted local setup or dependency work.

Example:

```text
Task: Add endpoint permission check for conversation item delete.

Current state:
- Conversation references exist.
- Item create/list/retrieve are implemented.

Goal:
- Delete must require explicit conversation item permission.
- Unknown or non-owned conversation IDs must return OpenAI-shaped 404 before provider forwarding.

Non-goals:
- Do not implement conversation update.
- Do not change Chat Completions.
- Do not add local content storage.

Tests:
- Add unit tests for permission denial.
- Add provider forwarding test proving no upstream call on non-owned ID.
- Run focused tests and ruff.

PR:
- New branch from main.
- Commit only related files.
- Open PR.
- Do not merge.
```

### Scope control

The most important section is often "Non-goals." Agents are trained to be helpful. Without explicit non-goals, helpfulness becomes scope creep.

Non-goals should name:

- features not to implement;
- files not to touch;
- APIs not to change;
- migrations not to create;
- dependencies not to add;
- tests not to skip;
- claims not to make.

For high-risk systems, constraints are not bureaucracy. They are part of correctness.

### Repair PRs

Sometimes a PR is open and needs repair. The next work order should not start a new feature if the current PR has failing CI, unresolved review comments, security concerns, documentation drift, or unanswered human questions about evidence.

Repair prompts should be narrower than feature prompts:

```text
Repair PR #123 only.
Do not add new feature behavior.
Read the failing CI logs.
Fix the minimum necessary issue.
Run the failing test locally.
Push to the same branch.
Report the exact failure cause and fix.
```

This keeps the project from accumulating half-valid work.

## IV.3 Verification and Validation Debt

AI coding reduces generation cost. It does not reduce the need for proof. In many cases it increases it, because generated code can be plausible, broad, and fast. OAP handles this by separating evidence collection from evidence presentation: the executor generates raw evidence, the strategic model compresses it, and the human interrogates the compressed result.

<ExpandingSideImg
  src="../assets/fig-05-validation-debt.svg"
  alt="Validation debt."
  caption="Validation debt."
/>

### What validation debt means

Validation debt is the review, testing, and reasoning burden created when code is generated faster than it can be understood. It is similar to technical debt, but it appears at the process level.

Validation debt accumulates when:

- large diffs are generated quickly;
- tests are shallow;
- the agent changes unrelated files;
- the report overstates certainty;
- reviewers trust style over substance;
- documentation claims more than code proves.

The solution is not to stop using agents. The solution is to constrain the work unit, demand evidence, and keep the human's review surface short enough to support real judgment.

### Tests as evidence

Tests are evidence only when they cover the claim. A unit test proves a narrow behavior. An integration test proves component interaction. An E2E test proves a user path. A browser smoke test proves that at least one visual workflow loads. None proves everything.

OAP reports should name test scope:

```markdown
Tests run:
- `python -m pytest tests/unit/test_policy.py`: 18 passed.
- `python -m pytest tests/integration/test_quota.py`: not run; no TEST_DATABASE_URL configured.
- `ruff check app tests`: passed.
```

This is better than:

```markdown
All checks passed.
```

### Skipped tests are unknown

One of OAP's most important rules is:

> A skipped test is not a passing test. A test that was not run is not evidence.

This rule should appear in the constitution. Agents often try to be helpful by summarizing partial success as success. That behavior must be corrected.

### Meaningful tests

Test quality matters. A test can be meaningless if it:

- asserts implementation details without checking behavior;
- only checks that a function returns something;
- mocks away the risk being tested;
- reproduces the current bug as expected behavior;
- uses generated expected output without independent reasoning.

The strategic layer should ask: if this feature were broken in the dangerous way, would the test fail? The human should be able to ask that same question and receive a concise answer with a pointer to the relevant test.

### Verification-only runs

Sometimes the next task should not be implementation. It should be verification. A verification-only agent prompt should forbid edits:

```text
This is a verification-only run.
Do not create a branch.
Do not edit files.
Do not commit.
Run the specified verification commands.
Report exact results, skipped tests, and blockers.
```

Verification-only runs are useful before releases, after large merges, or when the strategic layer suspects that reports are too narrow.

## IV.4 Security and Safety During Implementation

OAP assumes agents can be powerful enough to cause harm. Security rules must therefore be explicit, repeated, tested, and encoded in the constitution.

### Fail closed

Fail-closed behavior means that uncertain or unsupported states are rejected safely rather than passed through optimistically.

Examples:

- unknown pricing rejects a cost-limited request;
- unknown route capability rejects forwarding;
- non-owned resource IDs return not found before provider access;
- bad host keys stop an SSH workflow before credential entry;
- missing test database blocks integration claims;
- unsupported provider features return explicit unsupported errors.

Fail closed is a design posture. It is especially important when an execution agent might otherwise "make it work" by relaxing validation.

### Secrets

The agent runtime should not contain production secrets. The repository should not contain real provider keys. Logs should not contain credentials. Documentation should use placeholders.

The constitution should say:

```markdown
## Secrets
- Never commit real provider keys.
- Never store plaintext gateway keys.
- Never print tokens in test output.
- Never paste production secrets into prompts.
- Use fake placeholders in docs and tests.
- If a secret appears in output, stop and report.
```

For coding-agent systems, this is not optional. Prompt history, tool logs, shell history, test output, telemetry, and PR comments can all become accidental disclosure channels.

### Approval gates

Human approval is required for:

- production deployment;
- merge to protected branches;
- destructive data operations;
- credential rotation;
- public release claims;
- adding risky dependencies;
- widening network access;
- changing security posture.

Codex documents sandbox and approval layers as separate controls: sandbox mode determines what the agent can technically do; approval policy determines when it must ask [[15]](#ref-codex-security). OAP uses the same separation concept at the process level. The runtime boundary controls what can happen. The human gate controls what is accepted.

### Safety scans

For security-sensitive projects, execution reports should include scans such as:

```bash
rg "api_key|Authorization|Bearer|password|secret|token" app tests docs -n
git diff --check
python -m pytest tests/unit
ruff check app tests
```

The exact commands depend on the stack. The point is that safety checks should be named and repeatable.

### Avoiding unsafe helpfulness

Agents may try to:

- disable a failing test;
- loosen validation;
- add a broad catch-all;
- mock the wrong boundary;
- skip a hard integration path;
- use real services because mocks are inconvenient;
- make documentation sound more complete than reality.

The strategic layer must punish these shortcuts. In OAP, "working" is not enough. The change must work inside the project's rules.

## IV.5 Documentation, Handoffs, and Memory

AI workflows need durable memory. Chat transcripts are useful, but they are not enough. They become long, stale, unavailable, or hard to search. OAP treats documentation as operational memory for humans and agents. Documentation should also reduce reading load: short summaries should point to deeper details instead of forcing every future reader to reconstruct the project from chat.

### Documentation types

A mature OAP project often needs:

- README;
- quickstart;
- architecture overview;
- security model;
- compatibility matrix;
- deployment guide;
- runbooks;
- testing guide;
- release notes;
- review archive;
- remediation matrix;
- handoff documents.

Not every project needs all of these. But every serious project needs enough documentation for a new human, strategic model, or execution agent to continue safely.

### Handoffs

Handoffs solve context transfer. They should be written for the next strategic session, not for the end user. A good handoff should be short enough to reload context quickly while still pointing to durable evidence. It includes:

- current repository truth;
- recent merged PRs;
- open PRs;
- known blockers;
- implemented scope;
- missing scope;
- safety rules;
- next recommended task;
- tasks explicitly not recommended.

Handoffs should never be treated as authoritative over the live repository. They are snapshots. The first step after reading a handoff is verification.

### Documentation as contract

Documentation must track behavior. If an endpoint is implemented, the compatibility matrix changes. If a feature is deliberately unsupported, docs should say so. If a release is beta, docs should not imply production certification.

This is part of OAP's honesty discipline. Generated code can create the appearance of maturity quickly. Documentation must counterbalance that by stating actual scope.

### Runbooks

Runbooks are procedures for failure and operations:

- key rotation;
- compromised key response;
- database backup and restore;
- Redis outage;
- email ambiguity;
- admin lockout;
- deployment rollback;
- metrics alert response.

Agents can draft runbooks, but humans must ensure they do not invent commands or promise unsupported recovery paths.

<Question
  id="oap-pr-sized-delegation"
  question="Why does OAP prefer PR-sized delegation over broad, open-ended implementation tasks?"
  options={["Because pull requests eliminate the need for tests", "* Because PR-sized work keeps scope reviewable, preserves evidence, and limits context drift", "Because it allows the execution agent to own product strategy", "Because it removes the need for a strategic review brief"]}
  attempts={2}
>
PR-sized tasks are small enough to inspect and verify, but large enough to carry useful implementation context and durable evidence.
</Question>
