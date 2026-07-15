# Part III: Strategic Discovery and Constitution

## III.1 The First Conversation With the Strategic Model

The strategic layer is where OAP differs most from ordinary coding-agent use. Many workflows delegate a task directly to a coding agent. OAP inserts a reasoning layer before and after execution, and it makes that reasoning layer the human's main interface to the project.

The human should not normally manage the execution agent directly. Direct management is tempting because it feels precise: paste this error, run that command, inspect that file. But it consumes the human's scarce attention at the wrong level. This is especially important when the human is a domain expert rather than a professional developer. The strategic AI should absorb executor reports, inspect repository evidence, translate technical claims into domain-relevant terms, and answer the human's high-level questions.

Before the first strategic-model session, download [strategic_model_init_material.md](../../strategic_model_init_material.md), open a new chat, and choose a sufficiently capable model. Good choices are GPT-5.5 Thinking with thinking effort set to Extended, GPT-5.5 Pro, Claude Opus 4.8, or Claude Sonnet 4.6. If you use Claude, set effort to High or Max and turn Thinking on. Then upload the file and start with this instruction: "Read the attached text describing the OAP concept and tell me whether you can play the role of the strategic model." In OAP, this should be the first preparation step for the strategic model.

<Sidenote>
This is the chapter where OAP most clearly departs from ordinary coding-agent use: the strategic model is not a helper bolted onto execution, but the primary interface through which the human governs the project.
</Sidenote>

<ExpandingSideImg
  src="../assets/fig-08-strategic-discovery.svg"
  alt="Strategic discovery turns domain intent into executable project law."
  caption="Strategic discovery turns domain intent into executable project law."
/>

### The discovery conversation

Strategic discovery starts with the human's domain problem, not with a stack. The human asks the strongest available strategic model to determine what kind of software system is needed, which tools are appropriate, what professional rules should govern the work, and what the execution agent must not improvise.

The conversation should be explicit enough that a future `AGENTS.md` can be drafted from it. A useful sequence is:

1. State the domain problem in operational language.
2. Ask what kind of system this really is.
3. Ask which architecture and trust boundaries fit.
4. Ask which stack is boring, robust, and suitable.
5. Ask which data model, background jobs, admin flows, and tests a professional team would expect.
6. Ask what should be excluded from the first release.
7. Ask the model to convert the decisions into `AGENTS.md`, design docs, and first work orders.

The human does not need to know the answer in advance. The human needs to know the domain well enough to reject the wrong answer.

### API Gateway discovery example

The SLAIF API Gateway work demonstrates the pattern clearly. The opening human problem was not "write a FastAPI app." It was a training and governance problem: for SLAIF/WP6 workshops, participants needed LLM API access with bounded cost, auditable usage, and no exposure of real provider keys.

The strategic model first clarified the upstream limitation: ordinary provider API keys and project budgets were not enough for strict per-key hard quota. That shifted the product category. The system was no longer "a set of keys" or "a script for users." It became a controlled OpenAI-compatible gateway: users receive gateway-issued keys, use ordinary OpenAI SDK conventions, and the backend authenticates, checks quota, routes to providers, substitutes server-side provider credentials, records usage, and fails closed when policy or pricing is unknown. The public repository now reflects that product shape [[37]](#ref-slaif-repo).

The discovery chain looked like this:

| Domain question | Strategic translation | Resulting project decision |
|---|---|---|
| Can users have hard per-key OpenAI spend limits? | Native provider controls are insufficient for strict per-user workshop caps. | Build a local quota-enforcing gateway. |
| Can users keep ordinary OpenAI examples? | Compatibility matters more than custom naming. | Use `OPENAI_API_KEY` and `OPENAI_BASE_URL`; expose `/v1`. |
| How should keys be stored? | Treat gateway keys as bearer tokens and never store plaintext. | Store HMAC-derived token hashes with server-side pepper. |
| How can hard quota survive concurrency? | Estimate before forwarding and finalize after provider usage returns. | Implement reserve-then-finalize quota/accounting. |
| Which backend stack fits? | Async HTTP proxying, streaming, database transactions, and admin workflows are central. | FastAPI/Starlette, `httpx`, PostgreSQL, Redis/Celery, SQLAlchemy/Alembic. |
| How should admins manage workshops? | The system needs both web and terminal operations. | Server-rendered admin dashboard plus Typer CLI. |
| How should the executor be guided? | Architecture and invariants must be repository law before broad implementation. | Write `AGENTS.md`, schema docs, compatibility matrix, tests, and PR workflow. |

The important point is that the model did not merely answer syntax questions. It helped the domain expert discover the product category, then the architecture, then the implementation constitution.

### Human prompt examples

In the API Gateway chats, the human's prompts were short but managerial. They asked questions like:

```text
Is hard per-key spend control possible?

If not, can I build my own API server, issue my own keys,
do the accounting, and forward allowed requests to OpenAI?

Can the client remain the ordinary OpenAI Python client
with no code changes?

Before writing AGENTS.md, tell me how cost and token
accounting per key should work.

Now specify the building blocks and tools:
database, framework, admin UI, CLI, email, tests, deployment.

Should the database schema be placed in the repo before
the execution agent starts?
```

These are not low-level implementation prompts. They are management prompts. The human supplies domain intent, constraints, and acceptance pressure. The strategic model supplies architecture options and professional defaults. The execution agent later receives bounded work.

### Technical decisions produced by discovery

A good strategic model should make technical decisions legible to a domain expert. In the API Gateway case, the model explained not only what to use, but why:

- **FastAPI, Starlette streaming, Uvicorn/Gunicorn**: asynchronous API logic, Server-Sent Events pass-through, and production worker management.
- **PostgreSQL, SQLAlchemy async, asyncpg, Alembic**: durable quota/accounting truth, non-blocking database access, and reproducible schema evolution.
- **Redis and Celery**: short-lived coordination, rate limits, reservations, and background jobs such as email and reports.
- **Jinja2, HTMX, Tailwind, Typer**: simple admin dashboard and CLI without turning the project into a large frontend application.
- **pytest, pytest-asyncio, respx/pytest-httpx, testcontainers, Hypothesis, Playwright**: tests for async code, mocked upstream APIs, real database/Redis behavior, accounting invariants, and admin UI flows.
- **Docker Compose**: reproducible small deployment with API, database, Redis, worker, scheduler, and optional reverse proxy.

The domain expert did not need to know all these components beforehand. The human needed to interrogate whether each component served the domain goal: bounded workshop keys, provider-key secrecy, usage evidence, OpenAI-compatible examples, and release honesty.

### Discovery artifacts

The output of strategic discovery should be written down before the execution agent starts broad implementation. In a mature OAP project, discovery produces at least:

- a short architecture note;
- an `AGENTS.md` constitution;
- a data model or schema document;
- a compatibility matrix when external APIs are being emulated;
- a test strategy;
- a deployment sketch;
- a first PR-sized implementation sequence;
- explicit non-goals.

For the API Gateway, one decisive discovery artifact was the database schema. The strategic model advised putting a human-readable `docs/database-schema.md` into the repository before Codex implemented SQLAlchemy models and Alembic migrations. That is the right OAP reflex: make the strategic decision durable before asking the executor to produce code.

### Strategic responsibilities

The strategic layer should:

- understand the product goal;
- preserve domain assumptions;
- translate domain language into technical work orders;
- preserve the project's long-running context;
- identify missing assumptions;
- sequence work safely;
- choose the next narrow PR;
- write explicit work orders;
- interpret agent reports;
- compare results against the constitution;
- map claims to concrete evidence;
- answer the human's readiness questions;
- explain technical evidence in domain terms;
- decide whether to repair, continue, or stop;
- maintain project-state summaries;
- create handoffs when context grows too large.

The strategic layer is not necessarily one model forever. A project may use one model for planning, another for code review, another for documentation critique, and another for external audit. What matters is that the human lead controls when and why these models are consulted, and that one strategic thread remains responsible for the project story.

### Model selection and context economics

OAP should normally use the strongest practical model for the strategic layer. This means a model with strong reasoning, long context, reliable instruction following, good code comprehension, and enough patience to compare claims against evidence. The strategic model is where expensive tokens are most valuable.

The reason is context economics. The strategic model's context burns slowly. It contains:

- the product goal;
- domain vocabulary and constraints;
- architectural decisions;
- unresolved risks;
- previous PR outcomes;
- current release status;
- evidence trails;
- human preferences;
- handoff summaries;
- open questions.

The execution agent's context burns quickly because it reads files, edits code, sees command output, retries failures, and explores local state. That is acceptable. The executor only needs enough context to complete one PR-sized task. The strategic model should preserve continuity across many such tasks.

The desired operating state is:

- the strategic AI does not lose context;
- the human does not lose the goal;
- the execution agent does not need to remember beyond the current PR;
- durable state is written back into the repository, PRs, issues, docs, and handoffs.

### Strategic output: the work order

The strategic layer's most important output is not code. It is a work order that the execution agent can follow without improvising the product and without asking the human to perform low-level work. When the human is a domain expert, the work order is also a translation artifact: it turns domain intent into implementable software behavior while preserving acceptance criteria.

A good work order includes:

- current verified project state;
- exact task goal;
- domain behavior to preserve;
- acceptance criteria in domain language;
- files or areas to inspect;
- constraints and non-goals;
- required implementation behavior;
- tests to add or run;
- tools, dependencies, or local services the agent may install inside the execution VM;
- documentation updates;
- branch and PR instructions;
- final report format.

This is one reason OAP is not "prompt engineering" in the shallow sense. The prompt is a software management artifact. It encodes scope, risk, verification, and workflow.

### Strategic review of agent reports

After execution, the strategic layer reviews:

- Did the agent do the requested task?
- Did it do extra work?
- Did it touch unrelated files?
- Are the tests meaningful?
- Are skipped tests honestly reported?
- Did documentation change with behavior?
- Did the change preserve architecture?
- Did it introduce new risk?
- Did the agent ask the human to do work that belonged inside the execution VM?
- Is a repair prompt needed before merge?

The strategic model performs the first review pass and prepares answers for the human. The human must judge that review. A model can miss risks. A model can overpraise. A model can rationalize. The human lead must remain skeptical, but skepticism should be expressed as high-level interrogation:

- Show me the exact test evidence.
- Show me the files that enforce the invariant.
- Explain why this does not expose secrets.
- Explain why this dependency is necessary.
- Explain what would fail if the behavior were broken.
- Tell me what you are least confident about.

### Strategic continuity

Long projects need continuity. The strategic layer should periodically produce concise state handoffs. These are not just notes for humans. They are context-preservation artifacts for future strategic sessions:

```markdown
# Project Handoff

## Current truth
- Main branch state:
- Open PRs:
- Recently merged PRs:
- Known CI status:

## Product goal
- Current milestone:
- Release target:

## Implemented
- ...

## Missing
- ...

## Non-negotiable rules
- ...

## Next recommended task
- ...

## Do not do next
- ...
```

The handoff is not a substitute for verifying current repository state. It is a memory aid. Every new strategic session should treat the live repository as authoritative.

## III.2 Writing the Project Constitution

A project constitution is the durable rule set that tells agents how to work in the repository. In Codex, the direct mechanism is `AGENTS.md`: Codex reads such files before starting work and layers global, project, and nested instructions by precedence [[1]](#ref-codex-agents-md). In Claude Code, the analogous project instruction mechanism is `CLAUDE.md`, which Anthropic documents as persistent instructions loaded at the start of a session [[38]](#ref-claude-code-memory). Other tools use related mechanisms: repository custom instructions or rule files [[39]](#ref-github-copilot-agent); [[40]](#ref-cursor).

When a project may be worked by both Codex CLI and Claude Code CLI, keep `AGENTS.md` and `CLAUDE.md` aligned. They do not need to be word-for-word identical, but the operational law should be the same: mission, architecture, forbidden actions, tests, workflow, and final report requirements.

OAP treats the constitution as a first-class artifact.

<ExpandingSideImg
  src="../assets/fig-03-project-constitution.svg"
  alt="The project constitution as layered operational guidance."
  caption="The project constitution as layered operational guidance."
/>

### Discovery before constitution

The constitution should be written after strategic discovery, not before it. Otherwise `AGENTS.md` becomes a list of arbitrary preferences rather than the operational law of a real product.

A domain expert should first use the strategic model to explore:

- the product category;
- user workflow;
- operational constraints;
- security and privacy boundaries;
- plausible architectures;
- stack choices and alternatives;
- minimum viable release scope;
- explicit non-goals.

The result of that conversation becomes the constitution. The strategic model can draft it, but the human must judge whether it reflects the real domain. This is why the opening phase of OAP is managerial. The human is not asking, "write me Django code." The human is asking, "given this domain and these constraints, should this be Django, FastAPI, Go, a browser extension, a local agent, a queue-backed system, a signed-artifact system, or something else?"

### What a constitution is

A constitution is not a README. A README explains the project to users and contributors. A constitution instructs the agent how to behave while changing the project.

A constitution is not a single prompt. A prompt is temporary. A constitution persists across tasks and becomes part of the repository's operational memory.

A constitution is not merely style guidance. It should include architecture, safety rules, tests, documentation contracts, workflow, and definition of done.

### Minimum constitution structure

A serious OAP constitution should include:

```markdown
# AGENTS.md or CLAUDE.md

## Discovery Summary
- Domain problem.
- Chosen product shape.
- Architecture and stack rationale.
- Important alternatives rejected.
- First release scope.

## Mission
- What this repository is for.
- What user promise must not be broken.

## Architecture
- Main components.
- Stack and versions.
- Ownership boundaries.
- Data flow assumptions.

## Non-negotiable invariants
- Security rules.
- Privacy rules.
- Data retention rules.
- Backward compatibility rules.

## Forbidden actions
- Files or systems not to touch.
- Dependencies not to add.
- Secrets never to log or commit.
- Production resources never to access.

## Workflow
- Branch requirements.
- Commit requirements.
- Pull request requirements.
- No direct commits to main.

## Testing
- Required unit tests.
- Required integration tests.
- When browser/E2E tests are required.
- How to report skipped or blocked tests.

## Documentation
- Which docs must change with behavior.
- Where compatibility matrices live.
- How to state limitations.

## Reporting
- Required final report format.
- Required evidence.
- Required risk and follow-up section.
```

### Constitution as memory

Long AI-assisted projects suffer from context decay. Chat histories become too long. Uploaded files expire. Models forget details. A constitution counters this by putting stable project law in the repository.

The constitution should evolve when recurring corrections appear. If an agent repeatedly removes a required README block, add a rule. If an agent repeatedly claims skipped tests passed, add reporting language. If a security review finds a class of unsafe behavior, encode it as a forbidden action and a test requirement.

The official Codex documentation explicitly frames `AGENTS.md` as durable project guidance and recommends using it for build and test commands, review expectations, conventions, and recurring feedback [[1]](#ref-codex-agents-md). OAP extends that idea: for serious work, the constitution is the center of governance.

### Constitution smell tests

A constitution is too weak if:

- it only says "write good code";
- it does not name tests;
- it does not define forbidden behavior;
- it does not explain release or PR workflow;
- it does not mention secrets;
- it does not say what evidence the agent must report;
- it cannot help a new strategic model continue the project.

A constitution is too large if:

- it contains stale historical chat;
- it repeats documentation better kept elsewhere;
- it exceeds tool context limits;
- it contains contradictory rules;
- agents routinely ignore it because it is too diffuse.

The solution is layered guidance: top-level rules for the whole repo, nested rules for specialized directories, and separate docs for long background material.

## III.3 Work-Order Engineering

Prompting in OAP is not about clever phrasing. It is about work-order engineering. A work order turns strategic judgment into executable instructions. In mature OAP, the human does not usually write this prompt directly for the execution agent. The human explains intent and questions to the strategic AI; the strategic AI compiles the executor work order.

This aligns with current coding-agent practice: the durable setup, the real working directory, and the specificity of instructions matter as much as the model invocation itself [[41]](#ref-codex-best-practices).

### Work-order template

```markdown
# Coding Agent Work Order

You are working in repository: `<repo>`.

## Governing instructions
- Read `AGENTS.md` first.
- Follow repository workflow.
- If live repository state differs from this prompt, report the difference.

## Current verified state
- ...

## Goal
- ...

## Scope
- ...

## Non-goals
- ...

## Files to inspect
- ...

## Required behavior
- ...

## Tests required
- ...

## Local setup allowed
- Install missing test tools inside the execution VM if required.
- Document any package, browser, database, or service setup performed.
- Do not ask the human to perform routine dependency setup unless a safety boundary blocks it.

## Documentation required
- ...

## Workflow
- Start from fresh `main`.
- Create a feature branch.
- Commit only related files.
- Push branch.
- Open a pull request.
- Do not merge.

## Final report
- Branch.
- Commit.
- PR URL.
- Summary.
- Tests run and results.
- Local tools or dependencies installed.
- Docs changed.
- Risks or skipped tests.
```

### Current state must be current

The work order should not blindly trust an old handoff. It should say what is known and instruct the agent to verify. If the repository has moved, the agent should report it rather than building on stale assumptions.

This is especially important for long projects where multiple PRs are merged between chats. The strategic layer should verify current `main`, open PRs, and CI before drafting the next task. The human should be able to ask the strategic model "what is true now?" and receive an answer grounded in repository state, not memory alone.

### Non-goals as guardrails

Agents do not naturally understand product boundaries. They understand text. If a task should not touch a subsystem, say so. If a tempting feature is deferred, say so. If docs must not overclaim production readiness, say so.

Good non-goals are concrete:

- "Do not add a new database migration."
- "Do not change public API shape."
- "Do not store prompts or raw response bodies."
- "Do not run real upstream API calls."
- "Do not report skipped browser tests as passed."

### Report format as interface

The final report is the interface between execution and strategy. If the report is unstructured, the strategic model must reconstruct evidence manually and the human will be pulled toward low-level audit work. If the report is structured, the strategic model can answer high-level human questions faster and with less drift.

Reports should distinguish:

- passed;
- failed;
- skipped;
- not run;
- blocked;
- out of scope.

The phrase "all tests passed" should be avoided unless it literally means the requested or full relevant test suite passed. "Focused tests passed; integration tests were not run" is more useful.

### Prompt smells

A prompt is weak if it says:

- "make this better";
- "finish the feature";
- "fix all issues";
- "use your judgment" without constraints;
- "run tests" without naming which tests;
- "update docs" without naming the documentation contract;
- "ask me if dependencies are missing" without naming a safety reason.

A prompt is stronger if the strategic AI can determine success before the agent starts and the human can later interrogate the evidence without reconstructing the work manually.

<Question
  id="oap-strategic-discovery-first"
  question="According to the manual, what should happen before broad execution-agent implementation begins?"
  options={["The execution agent should improvise the architecture from the repository layout", "The human should manually install all likely dependencies first", "* Strategic discovery should define product shape, architecture, constraints, and constitution artifacts", "The project should skip work orders and go directly to a large implementation branch"]}
  attempts={2}
>
The manual insists that the strategic layer should discover the system shape and write durable operational law before the execution agent starts broad implementation.
</Question>
