# 3. Start With Strategic Discovery

Do not start by asking Codex CLI with `codex --yolo`, or Claude Code CLI with `claude --dangerously-skip-permissions`, to "build the app." Start by asking a strategic model what kind of system the domain problem requires.

This is the key move for domain experts. You may know the operational problem very well while not knowing the best architecture. The strategic model can help translate domain intent into technical shape.

Use a strong general model for this conversation. It can be ChatGPT, Claude, or another model with enough reasoning and context. This strategic conversation is not the execution run. Do it before launching the high-autonomy CLI agent.

First, download [strategic_model_init_material.md](../../strategic_model_init_material.md), open a new chat, and choose a sufficiently capable model. Good choices are GPT-5.5 Thinking with thinking effort set to Extended, GPT-5.5 Pro, Claude Opus 4.8, or Claude Sonnet 4.6. If you use Claude, set effort to High or Max and turn Thinking on. Then upload the file and start with this instruction: "Read the attached text describing the OAP concept and tell me whether you can play the role of the strategic model." In this workflow, that is the recommended first preparation step before this conversation.

Copy this prompt:

```text
I want to use Orchestrated Agentic Programming.

My domain problem is:
<describe the real operational problem>

Users are:
<who uses it>

Important constraints:
<security, privacy, cost, deployment, compliance, hardware, deadlines>

What kind of software system is this really?
Which architecture and stack fit?
What trust boundaries matter?
What should not be built in the first slice?
What tests would prove the first useful behavior?
What should go into AGENTS.md and CLAUDE.md before an execution agent starts?
What is the first PR-sized task?
```

Good strategic answers do not only name a framework. They explain:

- product category;
- data model;
- trust boundaries;
- boring and robust stack choices;
- operational risks;
- non-goals;
- first useful slice;
- what the execution agent should prove.

If the strategic model gives you a vague answer, push it:

```text
Be concrete. Name the architecture, stack, data model, first milestone,
forbidden actions, and tests. I need this to become AGENTS.md,
CLAUDE.md, and one execution work order.
```

The human decision is still yours. The model proposes; the human accepts, rejects, or redirects.
