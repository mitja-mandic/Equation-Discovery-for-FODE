# Part V: Review, Audit, and Release

## V.1 Review and Audit

Review is where OAP either becomes engineering or collapses into automation theater. The agent's output must be reviewed, but review does not mean the human must manually read every generated line as the default path. Mature OAP reviews through compressed evidence first and targeted inspection second.

### Strategic review brief

Every PR should produce a short strategic review brief for the human:

```markdown
## Decision Brief
Recommendation: merge / repair / reject / defer

Goal match:
- ...

Evidence:
- Test command and result:
- CI result:
- Key files changed:
- Documentation changed:

Risks:
- ...

Human decision needed:
- ...
```

The brief should be short enough to read quickly. It should not hide evidence. It should point to it. The human can then ask for expansion:

- show the exact test;
- show the changed invariant;
- explain the security implication;
- compare the PR against the original goal;
- identify what was not tested;
- identify what would make you reject this PR.

### Human review as management discipline

Human review should evaluate:

- diff scope;
- behavior;
- tests;
- security;
- documentation;
- migration safety;
- release claims;
- operator impact.

The reviewer should not only ask "does this compile?" The reviewer should ask "does this preserve the system's meaning?" The human can make that judgment from a decision brief, strategic questioning, targeted file inspection, and external audit when risk demands it. The human does not need to make line-by-line review the routine bottleneck.

### AI-assisted review

AI can help review, and in OAP the strategic AI is the default first reviewer. It should not be the final accountable reviewer. Useful AI review prompts include:

```text
Review this diff for:
- security regressions;
- missing tests;
- documentation drift;
- violations of AGENTS.md.

Prioritize concrete findings over praise.
```

AI review is particularly useful for:

- scanning for inconsistency;
- checking docs against behavior;
- finding missing negative tests;
- comparing PR claims with diff;
- preparing human review questions;
- compressing large diffs into short decision briefs.

Codex's GitHub integration is one public example of this direction: review behavior can be customized through repository instructions, and review prompts can focus the agent on concerns such as security regressions [[42]](#ref-codex-github).

### Cross-model audit

One useful OAP pattern is to build with one model family and audit with another. This does not make the audit objective, but it reduces one kind of circularity. A model that did not participate in implementation may notice different issues, especially around overclaiming, missing tests, security boundaries, accounting invariants, and documentation drift.

Cross-model audit should not be treated as a decorative final review. In a mature OAP project it is a cadence: build, audit, remediate, verify, and audit again when the risk profile changes. The public SLAIF API Gateway archive shows this pattern clearly. Reviews were preserved as project artifacts, findings were tracked in a remediation matrix, and later work connected findings to PRs and verification evidence [[43]](#ref-slaif-reviews-archive); [[44]](#ref-slaif-remediation-matrix).

Cross-model audit works best when the auditor sees:

- repository URL or snapshot;
- project goals;
- known limitations;
- test results;
- specific questions;
- no pressure to praise.

The human can use cross-model audit as management leverage: not to read more, but to ask better questions and decide where to inspect.

<Sidenote>
The point of audit cadence is not ceremony. It is to force periodic challenge of architecture, claims, and evidence before apparent completeness hardens into release overconfidence.
</Sidenote>

### Audit cadence

Cross-model audit should usually be invoked at these points:

- **Architecture audit.** After the constitution, initial scaffold, and first executable skeleton exist, but before many features accumulate.
- **Boundary audit.** After authentication, secrets, billing, quota, streaming, deployment, or other high-risk boundaries are introduced.
- **Maturity audit.** Before changing project language from prototype to beta, release candidate, or production-ready.
- **Follow-up audit.** After remediation PRs land, especially when the original finding touched security, accounting, or release claims.

Extra audit rounds are justified when:

- a broad refactor changes architecture or transaction boundaries;
- a feature introduces new trust boundaries or credential flow;
- tests pass but the strategic model cannot explain the proof clearly;
- documentation starts to claim more than the implementation supports;
- CI failures repeat in a pattern that suggests fragile design;
- a release decision depends on an assumption that has not been challenged;
- the human feels tempted to accept a result mainly because the agent sounds confident.

The SLAIF API Gateway Review 6.0 / RC1 audit is a good example of why this matters. The review classified the project as credible RC-beta for the implemented scope, but it also identified a concrete remaining hard-quota risk: input-token and cost pre-reservation could underestimate non-message Chat Completions fields such as `tools` and `response_format` schemas [[45]](#ref-slaif-review6). That finding became bounded remediation rather than a vague concern. The remediation matrix then tracked the fix for non-message input estimation, follow-up invariant tests, and production runbooks as separate work items with verification evidence [[44]](#ref-slaif-remediation-matrix).

### Audit loop mechanics

An audit round should produce artifacts that the project can use:

1. Freeze the current scope: branch, commit, release candidate, or repository URL.
2. State implemented scope and known exclusions.
3. Ask the auditor for findings, not encouragement.
4. Separate current-scope defects from future feature requests.
5. Add accepted findings to a remediation matrix.
6. Convert each current-scope finding into one or more PR-sized work orders.
7. Close findings only with tests, docs, code links, or release-note changes.
8. Preserve honest language: an audit is not certification unless it really is.

The important management move is step 4. External models often complain about features that were never intended for the current release. OAP does not blindly implement every audit comment. The human, with help from the strategic AI, classifies findings: real defect, missing test, documentation drift, future work, or rejected recommendation. The execution agent then receives only bounded work orders.

### External audit

For serious systems, external audit should be treated as a project artifact. Findings should be archived, mapped to remediation tasks, and closed with evidence. The point is not to collect flattering scores. The point is to create a review trail.

### Review comments as work orders

A review comment can become the next execution task. The strategic layer should convert it into a precise repair prompt:

```text
Address only the unresolved review comment about missing ownership checks.
Do not refactor unrelated code.
Add a regression test proving non-owned IDs do not reach the provider adapter.
Push to the existing PR branch.
Report changed files and tests.
```

## V.2 Release Readiness

Feature completion is not release readiness. A feature can exist and still be unsafe to ship. In OAP, release readiness is a management decision backed by technical evidence. The human owns the release criteria and asks the strategic AI to compress evidence into a decision-ready form.

<ExpandingSideImg
  src="../assets/fig-07-release-readiness.svg"
  alt="Release readiness requires more than implemented code."
  caption="Release readiness requires more than implemented code."
/>

### Completeness levels

OAP should distinguish:

- prototype complete;
- implemented for a narrow path;
- tested for expected path;
- tested for negative paths;
- documented;
- operationally recoverable;
- reviewed;
- release candidate;
- production ready.

These are different claims. A manual, README, or release note should not blur them.

### Readiness scoring

Readiness scoring can help if it is honest. Example:

| Dimension | Question |
|---|---|
| Functional completeness | Is the intended behavior implemented? |
| Architecture quality | Does it fit the system design? |
| Security posture | Are known risks controlled? |
| Test coverage | Do tests prove core and negative paths? |
| Documentation | Can users and operators understand scope? |
| Operational readiness | Can it be deployed, monitored, and recovered? |
| Release honesty | Are limitations stated clearly? |

Scores should not replace evidence. They summarize evidence.

### Release decision brief

Before a release decision, the strategic AI should prepare a short brief:

```markdown
## Release Decision Brief
Recommendation: release / do not release / release with limitations

Goal:
- ...

Release criteria:
- ...

Evidence:
- CI:
- Tests:
- Security:
- Documentation:
- Rollback:

Known limitations:
- ...

Decision required:
- ...
```

This brief lets the human act like a disciplined manager: short text first, direct questions second, targeted inspection third. The human should not have to reconstruct release readiness from raw PRs, logs, and scattered chat history.

<Sidenote>
In OAP, release language is part of technical correctness. A system can be implemented and still be misrepresented if its documentation or release claims outrun the evidence.
</Sidenote>

### Release gates

Before release, require:

- explicit release goal;
- explicit release criteria;
- clean working tree;
- all release-relevant CI green;
- no required tests skipped without explicit blocker classification;
- docs aligned with implemented scope;
- known limitations documented;
- security scans complete;
- migration and rollback notes ready;
- final human release decision.

### The danger of apparent completeness

Agentic coding can make a project look complete faster than it becomes coherent. It can add files, tests, docs, and UI elements rapidly. The human release manager must ask whether the pieces form a system.

Release readiness is the discipline of saying "not yet" when the diff looks impressive but the evidence is weak.

<Question
  id="oap-release-readiness"
  question="What does the manual treat as the key difference between feature completion and release readiness?"
  options={["Feature completion already implies production readiness", "Release readiness only depends on whether CI passed once", "* Release readiness is a management judgment backed by evidence, documentation, tests, and operational criteria", "Release readiness is determined entirely by the execution agent report"]}
  attempts={2}
>
The manual repeatedly distinguishes implemented behavior from supported, tested, documented, and operationally honest release claims.
</Question>
