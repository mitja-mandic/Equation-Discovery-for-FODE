# Part VI: Case Studies and Applications

## VI.1 Case Study: SLAIF API Gateway

This chapter uses a public project as an illustrative case: an OpenAI-compatible API gateway for issuing limited gateway keys while keeping upstream provider credentials protected [[37]](#ref-slaif-repo). The point is not the specific domain. The point is the workflow.

### Problem shape

The product problem was not "make an app." It was a serious system:

- OpenAI-compatible client behavior;
- gateway-issued keys;
- quota enforcement;
- provider routing;
- usage accounting;
- admin operations;
- secure key handling;
- deployment and operator documentation.

This kind of system is a good OAP candidate because it has clear invariants, many mechanical implementation slices, and high security risk. It is also a good example of why the human must move up the ladder: the important human work is not typing CRUD handlers, but managing invariants, release claims, security posture, and proof.

### Architecture discovery

The first management act was not asking an agent to generate endpoints. It was asking the strategic model what kind of system the domain problem required and which technical ingredients were appropriate. The human supplied the domain need: many users need practical LLM API access, but the institution must protect upstream provider credentials, enforce spending limits, account for usage, and operate the system safely. The strategic model translated that into an architecture: OpenAI-compatible gateway, server-side provider keys, gateway-issued keys, PostgreSQL-backed hard quota/accounting, Redis as optional operational throttling, admin workflows, background jobs, tests, and deployment documentation.

This is important because a domain expert can know the problem deeply without knowing the current best software stack. OAP uses the strategic model to bridge that gap. The human remains manager and domain authority; the strategic model proposes architecture and tradeoffs; the execution agent later implements bounded slices.

The same pattern appears in the DHCP/IPAM appliance example. The domain problem was not "make a DHCP web UI." It was "manage DHCP/IPAM/DNS state safely on replaceable Raspberry Pi edge appliances." Strategic discovery changed the software shape: server-side source of truth, outbound edge connections, signed desired-state artifacts, a minimal local apply helper, `dnsmasq` validation, rollback, audit logs, and a public view that must be a sanitized snapshot rather than hidden admin controls. That architecture is a management output before it is an implementation task.

### Constitution first

The early artifact was not code. It was a detailed implementation brief and governing instruction file produced from the strategic discovery phase. This allowed the execution agent to work inside constraints rather than discovering the architecture through improvisation.

The constitution encoded:

- stack choices;
- security rules;
- testing expectations;
- PR workflow;
- documentation requirements;
- no real provider keys;
- no plaintext gateway key storage;
- no overclaiming production readiness.

### PR sequence

The project advanced through many small PRs. Each PR implemented or hardened a slice: schema, key service, quota reservation, provider routing, admin UI, documentation, tests, runbooks, feature families, release verification.

This matters because agentic work becomes reviewable when it is sliced. A large autonomous implementation would have been much harder to trust. Slicing also protected context: the execution agent could focus on one task, while the strategic model and documentation preserved the larger story.

### Control plane in practice

The human-facing work was not continuous direct conversation with the execution agent. The useful human questions were management questions:

- Is the gateway still fail-closed?
- Which tests prove quota enforcement?
- What secrets could leak?
- What is implemented versus merely documented?
- What remains before release?

Those questions belong to the strategic layer. The strategic model turns them into work orders, review briefs, remediation lists, and release-readiness summaries. The execution agent turns work orders into branches, tests, and PRs.

### Audit and remediation

External model review was used to assess architecture, security posture, test coverage, documentation, and production readiness. Findings were turned into remediation work rather than treated as praise. The public review archive and remediation matrix matter because they make the audit loop inspectable rather than anecdotal [[43]](#ref-slaif-reviews-archive); [[44]](#ref-slaif-remediation-matrix).

The RC1 audit did not merely say the project was good. It made a management judgment: the implemented scope was credible as RC-beta, but not production certification, compliance attestation, or penetration testing. It also identified concrete remaining work, including non-message Chat Completions input/cost estimation, quota/accounting/reconciliation invariant tests, and production runbooks [[45]](#ref-slaif-review6). Those findings became bounded work:

- the non-message input estimation issue was fixed as a focused policy, pricing, quota, and provider-forwarding remediation;
- invariant tests were added for quota, accounting, reconciliation, idempotency, and safe ledger/audit metadata;
- operator runbooks were added for key rotation, leaked key response, HMAC and one-time-secret handling, backup/restore, reconciliation, Redis outage, PostgreSQL readiness, metrics, deployment troubleshooting, and RC-beta upgrades.

This demonstrates a central OAP claim: the human does not need to personally implement every fix, but the human must manage the quality loop. The human decides which audit findings are current-scope defects, which are future work, which require tests, and which release claims are allowed. The strategic AI converts that decision into precise work orders. The execution agent performs the implementation and verification. The repository preserves the evidence.

This is the OAP review loop:

1. Build with execution agent.
2. Review with strategic model.
3. Audit with external model or reviewer.
4. Ask human management questions about goal, risk, and release criteria.
5. Convert findings into PR-sized work.
6. Verify and document closure.

### Lessons

The case illustrates several general lessons:

- A coding agent can perform large amounts of implementation labor.
- The human does not disappear; the human becomes more managerial and more important at gates.
- Domain knowledge remains decisive: the human must understand why quota, provider-key isolation, user-key issuance, accounting, and workshop operations matter.
- The strategic model should compress evidence into short decision material.
- The execution environment should let the agent do setup work without recruiting the human.
- Documentation and runbooks are not afterthoughts.
- Tests become the language of trust.
- Release honesty prevents agentic velocity from turning into false maturity.

## VI.2 Applying OAP to Other Projects

OAP is not limited to API gateways. The method generalizes by pattern: identify the domain goal, write the constitution, slice work into PRs, keep the execution runtime disposable, preserve repository truth, and review through evidence. Public repositories can then be used as examples of use cases, not as proof that every project is finished or production-certified.

The examples below should be read in two layers:

1. the **general use case**, which is reusable guidance;
2. the **visible repository example**, where a public repository exists and illustrates the pattern.

Private or internal projects can still inform the pattern, but they should not be presented as public examples. If the repository is not visible, describe the use case without pretending there is a public URL.

### Concept demonstrations across examples

**Human as manager and domain expert.** Demonstrated in the API gateway, SLAIF Connect, and DHCP/IPAM appliance examples. The human supplied the product invariants: protect provider keys, do not collect SSH credentials, do not expose inbound Pi management, and keep release claims honest.

**Strategic discovery and tool selection.** Demonstrated most clearly in the API gateway and DHCP/IPAM examples. The human asked what kind of system was needed and which tools fit the domain; the strategic model translated that into gateway architecture, quota/accounting choices, server/control-plane boundaries, edge-agent boundaries, and safe first milestones.

**Constitution-first execution.** Demonstrated in the API gateway and DHCP/IPAM scaffold work. The agent received architecture, non-goals, security rules, tests, and report format before broad implementation.

**Execution agent as implementation labor.** Demonstrated by public PR sequences and branch names across the visible repositories. The executor handled repository edits, tests, docs, and PR mechanics while the human stayed focused on decisions.

**PR as the unit of work.** Demonstrated in the API gateway, SLAIF Connect, and DHCP/IPAM appliance examples. Work stayed reviewable, revertible, and attributable. Later audit findings could become narrow PRs rather than vague repair campaigns.

**Remote repository as project truth.** Demonstrated through public GitHub repositories and review archives. Durable truth lived in branches, PRs, docs, CI, review files, and remediation matrices rather than in a local agent VM.

**Cross-model audit and remediation.** Demonstrated in the SLAIF API Gateway review archive. External critique found release-relevant issues that were converted into remediation work with verification evidence.

**Release honesty.** Demonstrated by the SLAIF API Gateway RC-beta language. The project could claim RC-beta readiness for implemented scope without pretending to be production-certified.

**Validation debt management.** Demonstrated through tests, compatibility matrices, runbooks, and remediation matrices. Fast implementation was balanced by stronger proof, operator documentation, and explicit known limitations.

### Writing new software

General concept: OAP works well for greenfield software when the human can define a strong product goal and begin with strategic discovery. The first practical artifact may be a constitution, but the first intellectual artifact is the architecture discussion: what kind of system is this, which tools fit, where are the trust boundaries, and what should the first release not attempt?

The key management move is to avoid the "make me an app" prompt. The human should instead define:

- what the product is for;
- what kind of product category or architecture is appropriate;
- which tools and frameworks are plausible;
- what must never happen;
- what the first release is allowed to claim;
- how evidence will be checked;
- which pieces are intentionally out of scope.

Visible examples:

- **SLAIF API Gateway**: a public OpenAI-compatible gateway for institutional LLM access, quota enforcement, provider routing, usage accounting, and operator workflows [[37]](#ref-slaif-repo). It demonstrates greenfield OAP at serious-product scale: specification first, many PR-sized implementation slices, strong security invariants, broad tests, documentation, release notes, and external review.
- **Managed DHCP/IPAM Edge Appliance**: a public early-stage DHCP/IPAM edge-management repository [[46]](#ref-dhcp-web-interface-repo). This is not a finished-product example. It demonstrates how OAP should begin a risky infrastructure product: scaffold and trust boundaries first, not a rushed web UI that can mutate network infrastructure.

How the concepts helped:

- The human manager defined domain hazards that a generic coder might miss.
- The strategic model translated those hazards into architecture and tool choices.
- The constitution prevented unsafe shortcuts from becoming architecture.
- The first PRs created reviewable foundations rather than a large unreviewable implementation dump.
- The execution agent could work autonomously because the work was bounded.

### Taking over existing software

General concept: OAP is useful when an existing codebase, fork, research tool, or academic project has value but lacks professional structure. The method should not begin by rewriting everything. It should begin by asking what must be preserved, what is unsafe, what is accidental complexity, and what evidence proves a safe transition.

The strategic AI is especially useful here because it can compare the old system against the desired system:

- what is real product logic;
- what is prototype scaffolding;
- what is copied upstream code;
- what should become a dependency rather than owned code;
- what tests are needed before replacing behavior.

Visible example:

- **SLAIF Connect**: a public browser-based SSH and remote-compute access project [[47]](#ref-slaif-connect-repo). The project began around a fork/prototype of a well-known browser SSH stack, but the OAP analysis pushed it toward a cleaner architecture: a non-fork extension, pinned upstream `libapps` as a build-time dependency, a WebSocket-to-TCP relay, extension-side host policy, and the rule that the SLAIF service must not receive SSH credentials.

How the concepts helped:

- The human domain manager supplied the real invariant: SLAIF may orchestrate HPC work, but must not become the SSH credential holder.
- The strategic layer separated useful prototype knowledge from wrong long-term ownership.
- The execution plan avoided an uncontrolled fork by turning upstream code into a pinned dependency and SLAIF behavior into project-owned extension, relay, policy, and tests.

### Rewriting wrong-shaped or failed software

General concept: sometimes the old system is not merely incomplete; it encodes the wrong shape. In that case OAP should not ask the agent to patch indefinitely. It should freeze the old implementation as a reference, extract the domain invariants, write a new constitution, and rebuild in small PRs.

This is different from a casual rewrite. A rewrite under OAP needs:

- a clear reason the old architecture cannot carry the next stage;
- a list of behavior and domain knowledge to preserve;
- explicit non-goals for the new first milestone;
- testable migration checkpoints;
- a public or internal audit trail explaining the choice.

Visible example:

- **SLAIF Connect** again illustrates this pattern [[47]](#ref-slaif-connect-repo). The wrong-shaped path was maintaining a divergent general-purpose Secure Shell fork as the product. The OAP path preserved the real domain goal while changing the architecture: browser-side SSH remains, credentials stay local to the user and HPC server, the relay forwards encrypted bytes, and project-specific policy lives outside upstream source.

How the concepts helped:

- The human did not ask the agent to "finish the fork." The human managed the goal and accepted a strategic architectural correction.
- The strategic AI turned a messy fork question into a migration plan.
- The executor could then build the new path incrementally through scaffold, vendoring, relay tests, browser validation, signed policy, and pilot-readiness work.

### Hardening an existing serious system

General concept: OAP is not only for creation. It is also strong for hardening a system that already works but needs release discipline. At this stage, the human's management role becomes more important, not less. The question shifts from "can the agent build it?" to "what evidence permits us to claim readiness?"

Visible example:

- **SLAIF API Gateway** demonstrates audit-driven hardening [[37]](#ref-slaif-repo). The Review 6.0 / RC1 audit identified a real remaining quota/cost-estimation issue and recommended invariant tests and production runbooks [[45]](#ref-slaif-review6). The remediation matrix then tracked the resulting fixes and their verification evidence [[44]](#ref-slaif-remediation-matrix).

How the concepts helped:

- Cross-model audit challenged the project at the right level: architecture, accounting, security, tests, and release language.
- The human classified audit findings into current-scope remediation versus future work.
- The strategic AI converted findings into PR-sized prompts.
- The execution agent fixed, tested, documented, and reported.
- Release language stayed honest: RC-beta for implemented scope, not production certification.

### Infrastructure management products

General concept: infrastructure management products need extra caution because the agent can quickly build a dashboard that looks useful while hiding dangerous control channels. OAP should force the architecture to separate desired state, validation, privileged local apply, audit logs, and rollback before automation reaches real infrastructure.

Visible example:

- **Managed DHCP/IPAM Edge Appliance** [[46]](#ref-dhcp-web-interface-repo) demonstrates this conservative start, not a completed product. The public README describes a server-side control plane, outbound edge appliance communication, signed desired-state artifacts, a local privileged apply helper, and the rule that the Pi must not expose inbound management or run a root network-facing daemon.

How the concepts helped:

- The domain manager defined the infrastructure hazard before implementation.
- The agent was asked for scaffold and backend foundations first, not privileged deployment logic or production DHCP automation.
- The architecture made the local apply helper tiny, auditable, and separated from network communication.
- Public no-login views were treated as sanitized published snapshots, not hidden-button versions of admin APIs.

### Existing academic or domain software

General concept: academic and domain software often has useful algorithms or workflows but weak packaging, tests, CI, privacy defaults, documentation, release process, and operator experience. OAP can professionalize such software through staged work:

- write or revise `AGENTS.md`;
- inventory existing files and risks;
- fix privacy and credential defaults first;
- add focused tests before broad refactors;
- add CI and packaging;
- preserve scientific or domain semantics;
- move toward release checklists and reproducible workflows.

If the repository is private, do not list it as a public example. The pattern remains valid, but public readers should see it as guidance rather than as a named visible case study.

### When OAP is too heavy

OAP may be too heavy for:

- one-off scripts;
- throwaway prototypes;
- experiments with no long-term value;
- personal utilities with low risk;
- tasks where direct human editing is faster than defining the process.

The method has overhead. Use it when the overhead buys safety, continuity, or scale.

### When OAP is especially useful

OAP is especially useful when:

- the project has security constraints;
- the system has multiple components;
- documentation matters;
- the work spans many PRs;
- tests can prove behavior;
- a domain expert can judge intent but cannot implement everything by hand;
- the domain expert knows the problem but not the best current architecture or toolchain;
- users and domain experts are closer to the problem than available software engineers;
- release readiness matters.

<Question
  id="oap-case-study-pattern"
  question="What recurring pattern do the case studies use to apply OAP to real systems?"
  options={["Start with a broad autonomous implementation and infer the architecture later", "* Use domain-led strategic discovery, write a constitution, slice work into PRs, and review through evidence", "Avoid repositories and keep truth in the runtime environment", "Treat external audits mainly as marketing validation"]}
  attempts={2}
>
Across the case studies, the repeatable OAP pattern is strategic discovery first, bounded execution second, and evidence-backed review throughout.
</Question>
