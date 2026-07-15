# Part VII: Discussion and Doctrine

## VII.1 Failure Modes

OAP is designed around failure modes that appear repeatedly in AI-assisted software work.

### Hallucinated APIs and dependencies

Models can invent library methods, configuration flags, packages, or endpoint shapes. Package hallucination has been studied as a supply-chain risk because nonexistent packages can become attack targets if attackers publish them later [[48]](#ref-package-hallucination).

Mitigation:

- verify official docs for unstable APIs;
- run code;
- pin dependencies;
- avoid adding dependencies casually;
- test real import paths.

### Shallow tests

Agents can generate tests that assert the code they just wrote rather than the behavior that matters.

Mitigation:

- require negative tests;
- require tests that fail before the fix when practical;
- review mocks;
- ask whether the test protects the risk.

### Context drift

Long sessions drift. The model remembers old PR states, stale architecture, or expired decisions. OAP splits this risk: the strategic model should preserve long context, while the execution agent should not carry assumptions beyond one task.

Mitigation:

- verify current repository state;
- write handoffs;
- keep constitution current;
- prefer live source over chat memory.
- compact or reset the execution agent between PR-sized tasks.

### Weak strategic model

OAP fails if the strategic layer is too weak for the role. A cheap or short-context model may summarize confidently while missing architectural drift, security implications, or unresolved human goals.

Mitigation:

- use the strongest practical model for strategy;
- keep strategic context clean and long-lived;
- ask for explicit evidence mapping;
- use cross-model audit for high-risk decisions;
- write handoffs before context becomes brittle.

### Control inversion

Control inversion happens when the execution agent starts piloting the human. Symptoms include repeated requests for the human to install packages, run commands, paste logs, repair environments, or decide low-level implementation details that belong inside the execution VM.

Mitigation:

- give the agent enough privilege inside a hardened VM;
- keep production secrets and irreplaceable state out of that VM;
- require the agent to document local setup;
- rebuild disposable environments instead of manually nursing them;
- route human decisions through the strategic model.

### Excessive human reading burden

OAP fails if the human must read large diffs, long logs, and verbose reports for every small decision. That recreates the labor bottleneck at a different layer.

Mitigation:

- require short decision briefs;
- ask the strategic AI for conclusion, evidence, risk, and decision;
- drill down only when risk or uncertainty demands it;
- keep PRs small enough for strategic inspection;
- forbid vague reports that force reconstruction.

### Scope creep

Agents may implement neighboring features because they look related.

Mitigation:

- explicit non-goals;
- PR-sized tasks;
- reject broad diffs;
- repair scope before merge.

### Overclaiming

Agents and humans may overstate readiness. "Implemented" becomes "supported." "Focused tests passed" becomes "fully tested." "RC" becomes "production ready."

Mitigation:

- standard report vocabulary;
- release-readiness checklist;
- documentation review;
- external audit.

### Credential leakage

Agents can expose secrets through prompts, logs, commits, screenshots, or telemetry.

Mitigation:

- no production secrets in agent runtime;
- secret scans;
- fake placeholders;
- redacted telemetry;
- no raw prompt or payload storage unless deliberately designed.

### Human complacency

The final failure mode is human complacency. OAP fails if the human stops judging. The process can make it easy to feel productive while accepting too much. Moving into a management role does not mean becoming passive. It means running a stricter discipline over goals, release criteria, evidence, and risk.

Mitigation:

- slow down at gates;
- demand short evidence briefs;
- inspect deeper when evidence is weak;
- ask for external review;
- treat every merge as a human decision.

## VII.2 Practical OAP Doctrine

This chapter condenses the manual into doctrine: rules that can guide real projects.

### Core principles

1. **Human moves up the ladder.** The human is no longer primarily the coder; the human manages goals, criteria, risk, and release.
2. **Domain expertise can lead.** The best human lead may be the person who understands the domain, not the person who writes code.
3. **Start with strategic discovery.** Before coding, ask what kind of system is needed, which tools fit, and where the boundaries are.
4. **Human owns intent.** Never outsource product meaning.
5. **Human owns risk.** The model cannot accept liability.
6. **Human owns release.** The agent does not decide readiness.
7. **Human works from short decision material.** Strategic AI should compress detail into evidence-linked briefs.
8. **Strategic AI is the control plane.** Use the strongest practical long-context model for architecture discovery, technology selection, memory, critique, domain translation, work orders, and evidence.
9. **Execution agent is disposable labor.** Its context should last one PR-sized task.
10. **Strategy and execution are separate.** Planning and repository mutation should be different roles.
11. **The constitution governs.** Durable rules beat repeated reminders.
12. **Autonomy lives inside a rebuildable boundary.** High privilege is acceptable only in a hardened disposable runtime.
13. **Remote repository is truth.** The VM is disposable; branches, PRs, CI, docs, and handoffs are durable.
14. **The PR is the unit.** Work should be reviewable, revertible, and evidenced.
15. **Non-goals are safety tools.** Say what not to do.
16. **Tests are evidence, not ritual.** Match tests to claims.
17. **Skipped is not passed.** Unknown remains unknown.
18. **Documentation is part of the artifact.** Behavior and claims must align.
19. **Audit is normal.** External critique is not a failure.
20. **Release language must be honest.** Beta means beta.
21. **Velocity must not outrun judgment.** Faster coding increases validation responsibility.
22. **Never let the agent pilot the human.** If the human is doing routine setup for the agent, redesign the runtime.

### Minimum viable OAP

For a small serious project:

- hold a strategic discovery conversation;
- decide the product shape, stack, trust boundaries, and first release scope;
- create `AGENTS.md`;
- use a capable strategic model as the human-facing control plane;
- use a dedicated branch per task;
- write work orders with goal, non-goals, tests, report format;
- run focused tests;
- require a PR;
- produce a short decision brief before merge;
- human interrogates evidence before merge;
- keep a simple handoff file.

### Mature OAP

For a larger project:

- documented strategic discovery and architecture rationale;
- layered constitutions;
- dedicated execution VM;
- high-autonomy mode inside hardened rebuildable runtime;
- passwordless local setup privileges where safe;
- no production secrets or irreplaceable data in the VM;
- premium long-context strategic model;
- per-PR executor context reset or compaction;
- protected branches;
- CI gates;
- security scans;
- external model review;
- runbooks;
- release-readiness scoring;
- release decision briefs;
- final verification harness;
- archived audit findings.

### Team adoption

Teams should start with low-risk tasks:

- documentation improvements;
- test additions;
- small bug fixes;
- refactors with strong tests;
- internal tooling.

Then expand toward feature work once the team trusts:

- constitution quality;
- prompt templates;
- runtime isolation;
- strategic review discipline;
- decision-brief quality;
- CI coverage.

The goal is not to maximize autonomy immediately. The goal is to increase autonomy only where evidence and boundaries support it.

## VII.3 Conclusions

OAP changes where human attention belongs. The human no longer needs to be the person who installs every dependency, writes every boilerplate file, and follows every traceback. The human becomes the person who defines the goal, asks the strategic questions, decides acceptable risk, and demands evidence.

This is not a reduction in responsibility. It is a relocation of responsibility. The human is still accountable for what is released. The difference is that the human governs through architecture, constitution, work orders, tests, audits, and release decisions rather than through continuous low-level coding.

The durable lesson is simple:

```text
Strategic model: translate intent into architecture and evidence questions.
Execution agent: perform bounded implementation labor inside a disposable runtime.
Human manager: own goal, risk, release, and domain correctness.
Repository: preserve truth.
```

When this loop works, agentic programming becomes less like chatting with a code generator and more like managing a fast, disciplined implementation shop. When it fails, it usually fails by collapsing the hierarchy: the execution agent pilots the human, the strategic model rubber-stamps vague reports, or the repository stops being the source of truth.

The method is therefore not "trust the agent." It is "design the control system so the agent can be useful without being trusted as the final authority."

<Question
  id="oap-doctrine-antipilot"
  question="Which statement best matches the manual's anti-pilot doctrine?"
  options={["The human should do routine setup for the agent so the agent can stay simple", "The strategic model should approve its own evidence without human scrutiny", "* The execution agent should not direct the human through low-level chores; the control system should be designed so that the human stays at the decision layer", "If the agent sounds confident, the control loop is working correctly"]}
  attempts={2}
>
The manual's anti-pilot rule is explicit: if the execution agent starts directing the human through routine low-level work, the control loop has inverted and the workflow should be redesigned.
</Question>
