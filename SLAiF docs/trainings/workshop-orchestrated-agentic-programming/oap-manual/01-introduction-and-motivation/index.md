# Part I: Introduction and Motivation

## I.1 Why OAP Exists

AI-assisted coding has moved through several recognizable stages. The earliest widely adopted form was completion: the tool predicted the next token, line, or small block inside the editor. The human remained fully inside the code-writing act. The tool accelerated typing and sometimes suggested APIs or idioms, but it did not own a task.

The next stage was AI pair programming. GitHub Copilot popularized the framing of an "AI pair programmer" and made generated code suggestions part of everyday editor work [[9]](#ref-github-copilot). Controlled research on GitHub Copilot found a substantial speed improvement on a bounded programming task, with the treated group completing the task 55.8 percent faster than the control group [[10]](#ref-copilot-productivity). That result matters, but its scope also matters: it studied a specific task shape, not the whole problem of shipping reliable software.

Chat-based coding changed the interface. A developer could explain intent in natural language, ask for design alternatives, paste errors, request tests, and iterate conversationally. This made AI useful outside the editor. It also created a new failure mode: code could look coherent in conversation while remaining untested, unreviewed, or incompatible with the actual repository.

The current stage is agentic software delivery. Coding agents can inspect a repository, edit multiple files, run commands, execute tests, and work against issue or pull-request workflows. SWE-bench made real GitHub issue resolution a central benchmark for this movement, with a public repository that helped standardize benchmark access and reproducibility [[11]](#ref-swebench-paper); [[12]](#ref-swebench-repo). SWE-agent showed that the interface between agent and computer materially affects agent performance, not merely the model behind the agent, and its open repository made that agent-computer-interface work inspectable [[13]](#ref-sweagent-paper); [[14]](#ref-sweagent-repo). Human-in-the-loop systems such as HULA show that there is practical and research interest in agents that plan, code, and raise pull requests while keeping engineers involved at checkpoints [[2]](#ref-hula).

OAP belongs to this later stage. Its concern is not completion quality alone. Its concern is the whole delivery loop:

- who defines the goal;
- who turns the goal into a safe plan;
- who operates the repository;
- what boundaries contain the executor;
- what evidence proves work was done;
- who reviews that evidence;
- who decides whether software is ready.

<Sidenote>
The key transition described here is from local code assistance to governed delivery. OAP begins where “the code looks plausible” stops being a sufficient success condition.
</Sidenote>

The center of gravity has shifted from "help me type code" to "help me operate a software delivery process." That shift is why OAP needs to be described as an operating discipline rather than as a prompting trick.

### The widening loop

Each generation of tool widened the loop:

| Stage | Human activity | AI capability | Main risk |
|---|---|---|---|
| Completion | Writes code directly | Suggests local continuations | Wrong or insecure snippet accepted quickly |
| Pair programming | Co-edits and asks questions | Suggests, explains, refactors | Plausible answers without repository proof |
| Chat-based coding | Describes tasks and errors | Generates files, tests, designs | Context drift between chat and repo |
| Coding agent | Delegates repo task | Edits, runs commands, tests | Autonomy without governance |
| OAP | Orchestrates delivery loop | Strategic critique plus execution labor | Human rubber-stamping of weak evidence |

OAP is not a rejection of previous stages. It uses them. The strategic model is often chat-like. The execution agent may expose IDE-like operations. The difference is that the work is organized around accountable delivery.

## I.2 Core Concepts of OAP

OAP should be understood first as a control system. Its purpose is not to make the human type less while staying trapped in the same low-level workflow. Its purpose is to keep human attention on intent, risk, proof, and release while delegating implementation labor to machines that can move faster than humans.

<ExpandingSideImg
  src="../assets/fig-00-oap-control-plane.svg"
  alt="The OAP control plane."
  caption="The OAP control plane."
/>

### Start with strategic discovery, not code

An OAP project should begin with a strategic discovery conversation, not with the execution agent and not with a blank repository prompt. The first question is not "what code should the agent write?" The first question is "what kind of system should exist?"

This is especially important when the human is a domain expert rather than a professional software architect. The human may know the operational need precisely: an institution must issue limited LLM API keys, a laboratory must manage workflows, a teacher must grade exams, an HPC service must launch jobs without receiving SSH credentials, or a Raspberry Pi appliance must apply DHCP configuration safely. That does not mean the human knows the right stack, trust boundary, data model, background-job system, browser-extension model, or deployment shape.

The strategic model helps the human ask and answer:

- What is the real product category?
- Which existing tools or architectures solve nearby problems?
- Which stack is boring and safe enough for this domain?
- Which components should be separate because the trust boundaries differ?
- Which parts should be postponed because they are too risky for the first slice?
- What must the execution agent never be allowed to improvise?

This is a management act. The strategic model proposes architectures and explains tradeoffs. The human accepts, rejects, or redirects based on domain knowledge. Only after this discovery does OAP produce the constitution and first execution prompt.

### The human owns the goal, not the terminal

The human's most important job is to keep the project pointed at the right problem. OAP therefore moves the human up the organizational ladder. The human is no longer primarily the coder and often not even the active software engineer in the day-to-day implementation sense. The human is acting more like a product owner, engineering manager, technical director, or accountable reviewer of evidence.

This is not just a change in tools. It is a change in role. The human manages intent, risk, priorities, and acceptance. This management role must be disciplined, not ceremonial: the human defines goals, acceptance criteria, release criteria, non-goals, budget of risk, and proof standards. But the human should do this with shorter texts, tighter summaries, and fewer low-level artifacts to inspect. The strategic AI manages translation, memory, compression, and technical synthesis. The execution agent manages code production inside a bounded environment.

The human asks:

- What are we trying to build?
- What must not be broken?
- What did we actually implement?
- Where is the proof?
- What risks remain?
- What should happen next?

The human should usually ask these questions of the strategic AI, not of the execution agent directly. Direct agent supervision is expensive because it pulls the human back into command-by-command work. If the agent says it needs a package, a compiler, a browser driver, a database fixture, or a local service, the preferred OAP answer is not "ask the human to install it." The preferred answer is "the agent installs or configures it inside the hardened execution space and reports what changed."

The strategic AI should answer in compressed form first: conclusion, evidence, risk, and next decision. The human can then drill down into files, logs, tests, or PR lines only when the summary is weak, the risk is high, or the answer does not make sense.

### The human can be the domain expert

The human in OAP does not have to be a professional software engineer. In many cases the best human lead is the domain expert: the physician, teacher, scientist, infrastructure operator, compliance specialist, manufacturing engineer, researcher, librarian, or public-sector process owner who understands the problem better than a software team ever will.

This is related to end-user software engineering and citizen development, but it is not the same shape. Traditional end-user development often asks the domain expert to become the builder, using spreadsheets, scripts, low-code tools, or AI-assisted prompts. OAP moves differently: the domain expert becomes the manager of an agentic delivery system. The strategic AI translates domain intent into technical work orders. The execution agent builds. The domain expert judges whether the resulting system serves the real domain need.

This matters because software often fails in translation. Requirements move from users to analysts, from analysts to tickets, from tickets to engineers, from engineers back to reviewers, and finally back to users. Every handoff can lose domain meaning. OAP can shorten that loop. The person closest to the domain can ask the strategic AI:

- Did we implement the workflow the users actually need?
- Does this match the real operational constraint?
- What assumption did the agent make about the domain?
- Which acceptance criterion proves the domain behavior?
- What would make this unsafe or useless in practice?

The domain expert does not need to inspect every class or function. The domain expert needs disciplined control over goals, acceptance criteria, release criteria, and evidence.

### Strategic AI turns domain intent into architecture

One of the most important OAP moments happens before the execution agent touches the repository. The domain expert asks the strategic model questions such as:

- What kind of system do I actually need?
- Which architecture fits this operational problem?
- Which tools, frameworks, databases, runtimes, and protocols are appropriate?
- Which parts are risky enough to isolate?
- What should be built first, and what should explicitly wait?
- What would a professional software team worry about here?

This is where modern high-reasoning models are especially useful to non-software-specialist domain experts. A domain expert may understand the real workflow, failure costs, policy constraints, and user pain, but not know the current software architecture landscape. The strategic model can act as an architecture translator and technology scout: it maps the domain problem into plausible software shapes, explains tradeoffs, identifies standard components, and proposes an implementation sequence that the execution agent can later follow.

This does not make the model the architect of record. The model can be wrong, outdated, or overconfident. The human still owns the goal and must challenge the answer. But without this initial strategic discussion, OAP becomes weaker: the execution agent may build from a shallow prompt instead of from a domain-informed architecture.

### Strategic AI is the control plane

The strategic AI is the human's main interface to the project. It translates human intent into architecture, tool choices, work orders, review questions, and release evidence. It interprets agent reports, compares evidence against goals, and prepares the next narrow task. It should be a strong, long-context model because it is not supposed to burn context on thousands of file edits. Its context is spent slowly: human discussion, project state, PR summaries, architectural decisions, risk registers, and evidence questions.

In an ideal OAP workflow, the strategic model almost never forgets the project. That ideal is not fully realistic, but it is the direction of travel. The workflow should preserve strategic context as long as possible, refresh it with handoffs when necessary, and avoid wasting it on mechanical implementation.

### The execution agent is disposable labor

The execution agent is valuable because it can operate the repository at machine speed. It reads files, modifies code, installs dependencies, runs tests, starts services, writes docs, commits, and opens PRs. It does not need to carry the whole project in its context forever. It needs enough context to complete one sliced task and return evidence.

This creates a useful asymmetry:

- the strategic AI should be the strongest practical model, with long context and high reasoning quality;
- the execution agent can be cheaper, faster, or both;
- the execution agent's context should last one PR-sized task;
- after the PR, the execution context can be compacted, reset, or discarded;
- the durable truth must live in the remote repository, PR discussion, CI logs, documentation, and handoff summaries.

### High privilege belongs in a hardened, rebuildable VM

Restricting an agent so strongly that it cannot install tools, rebuild libraries, run migrations, launch local services, or repair its own test environment often wastes human time. Modern coding agents are fast enough that one missing dependency can turn into hours of human work: chasing package versions, rebuilding native tools, setting up databases, or relaying terminal output. At that point OAP degenerates into the opposite of its purpose: the AI is piloting the human.

The preferred pattern is a hardened execution space that the agent may control extensively and that the project can afford to lose. The VM should contain no production secrets, no irreplaceable state, and no uncommitted project truth. If the agent breaks it, the VM can be rebuilt from the remote repository and documented setup commands. This makes high privilege safer than a fragile locked-down environment that constantly recruits the human for chores.

### The remote repository is project truth

OAP depends on a sharp distinction between disposable runtime state and durable project truth. The execution VM is temporary. The remote repository, branch, PR, CI log, tests, docs, issue trail, and release notes are durable. A local VM can be destroyed. A bad branch can be abandoned. A failed PR can be closed. But the project truth must remain visible, versioned, reviewable, and reconstructable.

This principle is what makes high-autonomy execution tolerable. The agent may be powerful inside the box because the box is not the source of truth.

### Review becomes evidence interrogation

OAP does not require the human to manually read every line of every PR as the default workflow. That can be as wasteful as installing dependencies by hand. The human instead interrogates the strategic model:

- Did we implement the requirement exactly?
- Which files changed and why?
- Which tests prove the critical behavior?
- What negative path did we test?
- Did the agent touch secrets or production-like data?
- Did docs overclaim readiness?
- What would make this PR unsafe to merge?

Manual code inspection remains available for high-risk areas, unclear reports, security-sensitive changes, or suspicious diffs. But the default human posture is not line-by-line labor. The default posture is adversarial questioning of the strategic AI's evidence map.

### Work is sliced so context does not collapse

PR-sized delegation is not only a Git habit. It is a context-management mechanism. A sliced task keeps the execution agent's context short enough to finish reliably. It keeps the strategic AI's context clean enough to remember the goal. It keeps the human's attention on decisions rather than implementation clutter.

The target state is simple: the strategic AI does not lose context, the human does not lose the goal, and the execution agent does not need to remember anything beyond the current task.

### The project constitution is machine-readable governance

The project constitution, usually `AGENTS.md` or an equivalent instruction file, converts repeated human correction into durable operational law. It tells agents how to behave when the human is not watching. It defines architecture, tests, security rules, forbidden actions, reporting requirements, and the definition of done.

Without a constitution, OAP decays into a sequence of clever prompts. With a constitution, every prompt inherits project law.

### Validation debt is the main debt

AI coding makes code cheap. It does not make correctness cheap. The faster agents generate implementation, the more the bottleneck moves to proof: tests, CI, architecture checks, security review, documentation accuracy, and release honesty. OAP is therefore not primarily a productivity trick. It is a validation-management method.

The strategic AI should help carry that validation burden. The human should not accept "done" as a feeling. The human should demand evidence through the strategic control plane.

### The anti-pilot rule

The most compact rule of OAP is this:

> The human pilots the strategic AI; the strategic AI directs the execution agent; the execution agent operates the machine. If the execution agent starts directing the human through low-level work, the control loop is inverted and must be redesigned.

## I.3 What OAP Is

Orchestrated Agentic Programming is a workflow in which a human lead coordinates at least three layers:

1. **Human intent and judgment.** The human defines the product goal, constraints, risk tolerance, and release decision.
2. **Strategic AI.** A high-reasoning, long-context model acts as architect, planner, reviewer, critic, memory layer, and prompt compiler.
3. **Execution agent.** A coding agent operates inside a bounded, rebuildable machine environment, edits the repository, installs tools, runs tests, creates commits, and opens pull requests.

<ExpandingSideImg
  src="../assets/fig-01-oap-loop.svg"
  alt="The OAP operating loop."
  caption="The OAP operating loop."
/>

The decisive design choice is that the strategic model and the execution agent are not fused into one uncontrolled loop, and the human is not dragged into agent babysitting. The human normally interacts with the strategic AI. The strategic AI converts human intent into work orders, reads execution reports, maps claims to evidence, and explains risk. The execution agent performs work and returns evidence. The human accepts, rejects, redirects, or releases based on strategic interrogation, not on trust in the executor's confidence.

### A working definition

**Orchestrated Agentic Programming is a human-governed, constitution-driven subtype of agentic software engineering in which a long-context strategic AI serves as the control plane, a high-autonomy coding agent executes in a hardened and rebuildable machine environment, and the human preserves goal, risk, evidence demands, and release authority.**

This definition is deliberately strict. A single chatbot conversation is not OAP. A coding agent making a patch is not enough. A multi-agent swarm without human gates is not OAP. A human manually carrying out the agent's setup chores is also not mature OAP. The method requires role separation, durable rules, bounded autonomy, rebuildable execution, evidence, strategic memory, and human accountability.

### Why "orchestrated"

The word "orchestrated" is useful because the human is not merely prompting. The human is arranging roles, timing, constraints, feedback, evidence, and context economics. A software orchestrator does not type every line, install every dependency, or read every generated line by default. The orchestrator is responsible for the system that emerges and for the questions that force the strategic model to prove the system is coherent.

This distinction matters. In low-discipline AI coding, the human often keeps asking for fixes until the demo appears to work. In inverted agentic workflows, the agent keeps asking the human to run commands, install packages, paste logs, or decide low-level repairs. In OAP, the human defines the task boundary, forbidden shortcuts, and evidence requirements; the strategic model translates those into execution; and the execution environment is powerful enough that the agent can do the low-level work itself.

### Why "agentic"

The method assumes the executor can act. It reads files, changes code, runs commands, observes failures, and adapts. This is a different class of activity from generating a code block in chat. Official Codex documentation, for example, distinguishes sandbox and approval settings that determine what an agent can technically do and when it must ask before acting [[15]](#ref-codex-security).

OAP can be practiced with cautious approval settings, or in high-autonomy modes when the runtime is deliberately bounded. The stronger claim is not "always use full autonomy." The stronger claim is "if you grant autonomy, move safety into the runtime boundary, project constitution, PR discipline, and strategic evidence loop." A high-privilege agent inside a disposable VM can be safer and more productive than a weakly empowered agent that repeatedly recruits the human for operational chores.

### Why "programming"

Programming does not disappear. It moves. The system still consists of code, tests, migrations, configuration, documentation, and deployment scripts. The difference is that the human no longer has to be the primary typist or the agent's terminal assistant. The human programs the process: intent, architecture, constraints, work orders, evidence demands, and decisions.

### What OAP is not

OAP is not vibe coding. Vibe coding is useful as a term for informal natural-language-led software creation where the developer may accept results based on feel. OAP moves in the opposite direction: more explicit constraints, smaller units, more tests, stronger review, and more honest readiness language.

OAP is not ordinary AI pair programming. Pair programming keeps the human inside the implementation loop. OAP can remove the human from most typing and command execution, while increasing the human role in strategy and validation.

OAP is not fully autonomous software engineering. Marketing around "AI software engineers" often emphasizes independent execution. OAP emphasizes governed execution. The agent may have high autonomy inside the machine, but it does not own product meaning or release authority.

## I.4 The Human Role Shift

The most uncomfortable question in OAP is: if the human does not write most of the code and does not manually supervise every agent step, what exactly does the human do?

The answer is that the human moves from implementation labor to management responsibility. This is not a demotion. It is a more abstract and often more difficult role. In mature OAP, the human is no longer primarily a coder. The human may be a product owner, engineering manager, technical lead, release manager, domain expert, or accountable decision maker. In many OAP projects, domain expertise matters more than coding expertise because the execution agent can produce code, while only the domain expert can judge whether the product is useful, safe, and faithful to the real workflow. That role can and must run a strong discipline: clear goals, explicit release criteria, acceptance thresholds, non-goals, risk posture, and evidence requirements. The human must understand enough about the domain, architecture, security, tests, and deployment to interrogate whether the system still makes sense. The human does that primarily through the strategic AI, not by becoming a slow manual wrapper around the execution agent.

<ExpandingSideImg
  src="../assets/fig-02-role-separation.svg"
  alt="Role separation in OAP."
  caption="Role separation in OAP."
/>

### The human lead

The human lead owns:

- the problem definition;
- product purpose;
- domain truth;
- user needs;
- ethical and legal boundaries;
- risk appetite;
- prioritization;
- acceptance criteria;
- release decisions;
- responsibility when the result is wrong.

These cannot be delegated to a model. A model can help articulate them. It can challenge inconsistencies. It can produce checklists. It can compare alternatives. But responsibility remains with the human or organization using the method.

The human lead also decides when the strategic answer is not good enough. This is central. An execution agent can produce a clean diff, passing tests, and a persuasive report while still solving the wrong problem. A strategic model can summarize that report and still miss a domain risk. Only the human lead can decide whether the result serves the intended purpose.

The human lead should ask the strategic AI uncomfortable questions:

- Did we implement the exact requirement or only something adjacent?
- Does this match the domain workflow users actually follow?
- Which test would fail if the critical behavior regressed?
- Did the agent touch any secrets, migrations, credentials, or deployment files?
- What files changed for reasons not directly tied to the work order?
- What evidence would you show to a skeptical external reviewer?
- What would you refuse to merge?

These questions are higher leverage than asking the execution agent to explain every command while it is working.

### The strategic AI

The strategic AI is not used primarily as a code generator. It is the control plane and memory layer. Its jobs include:

- helping the domain expert discover the right software shape;
- comparing architecture and stack options;
- turning broad intent into architecture;
- identifying missing requirements;
- proposing safe implementation order;
- writing work orders for the execution agent;
- reviewing execution reports;
- spotting documentation drift;
- identifying security and testing gaps;
- preparing handoff material;
- estimating release readiness.

The strategic AI should be allowed to think, criticize, and disagree. It should not be reduced to a prompt beautifier. In OAP, the strategic model is closest to a staff engineer, architect, technical program manager, and reviewer combined. It is still not accountable. It is an advisory and synthesis layer.

Because the strategic model carries project continuity, it should be the strongest practical model available: high reasoning quality, long context, strong instruction following, and good ability to compare claims against evidence. This is the place to spend expensive model capacity. The strategic model is not burning context on repetitive file edits or local retries; it is preserving the project story, the domain assumptions, and the human's goal.

### The execution agent

The execution agent is the implementation labor. It should not decide the product. It should not silently expand the scope. It should not merge its own pull requests. It also should not routinely ask the human to perform environment setup on its behalf. Its job is to execute a bounded work order:

- inspect relevant files;
- install or configure required local tools inside the execution VM;
- make a scoped change;
- run requested tests;
- update documentation as required;
- commit only related files;
- open a pull request;
- report exactly what happened.

The execution agent is valuable because it can do tedious work at machine speed. It can also do incorrect work at machine speed. That is why OAP pairs high autonomy with narrow scope and evidence requirements. The executor's context only needs to last one PR-sized task. After that task, it can be compacted, reset, or replaced.

### The new human skill stack

OAP increases the value of:

- requirements thinking;
- architectural judgment;
- security thinking;
- test design;
- evidence interrogation;
- debugging from reports;
- release management;
- documentation discipline;
- prompt/work-order design;
- knowing when not to delegate.

It decreases the relative importance of remembering every framework idiom by heart and the value of doing setup chores manually. It does not remove the need to understand software.

### What happens to implementers

The statement that the human moves up the ladder is clearest for the person who controls the OAP loop. It is less automatic for the people whose previous work was line-level implementation. OAP adoption should not pretend that implementation labor remains unchanged. Some of that work is compressed. Some of it is automated. Some of it becomes more valuable because the system now needs stronger validation, review, operations, and domain translation.

In a healthy adoption, implementers move toward higher-leverage roles:

- translating domain intent into precise acceptance criteria;
- designing tests and fixtures that prove behavior;
- reviewing architecture, security, privacy, and operations risk;
- maintaining the agent runtime, project constitution, and CI gates;
- turning audit findings into bounded work orders;
- inspecting high-risk diffs rather than reading every generated line;
- owning release engineering and incident runbooks.

In an unhealthy adoption, implementers are simply removed from the loop and the remaining human rubber-stamps agent output. That is not mature OAP. The method works only when the work formerly spent on typing and routine setup is reinvested into judgment, evidence, domain correctness, security, and release honesty.

### The temptation to rubber-stamp

The main human failure mode is rubber-stamping. The agent returns a confident report. The tests look green. The PR exists. The strategic model summarizes it fluently. The human wants progress. The temptation is to accept.

OAP must train the opposite reflex: treat every report as a claim, not proof. Ask the strategic model to point to evidence. Ask whether the tests cover the risk. Ask whether the docs overclaim. Ask whether the change made the system conceptually cleaner or merely more complete-looking. Inspect the diff directly when the evidence is weak, the risk is high, or the strategic answer does not withstand questioning.

<Question
  id="oap-intro-control-loop"
  question="In OAP, what is the preferred role of the human once the workflow is mature?"
  options={["To manually supervise every dependency installation and command", "To let the execution agent decide release readiness", "* To own intent, risk, evidence demands, and release decisions while delegating implementation labor", "To replace the strategic model as the main architecture memory"]}
  attempts={2}
>
The central role shift in OAP is upward: the human stops acting as the agent's terminal assistant and instead governs goals, evidence, and release authority.
</Question>
