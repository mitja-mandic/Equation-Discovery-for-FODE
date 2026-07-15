---
title: "Orchestrated Agentic Programming Manual (EN)"
subTitle: "A Human-Governed Workflow for Strategic AI, High-Autonomy Coding Agents, and Review-Ready Software Delivery, Version 1.0.1"
language: "en"
tocInHeader: true
chapters:
  - ./01-introduction-and-motivation
  - ./02-operational-preflight
  - ./03-strategic-discovery-and-constitution
  - ./04-coding-and-verification
  - ./05-review-audit-and-release
  - ./06-case-studies-and-applications
  - ./07-discussion-and-doctrine
  - ./08-appendices
---

**Author:** Janez Perš  
**Email:** janez.pers@fe.uni-lj.si  
**Version:** 1.0.1  
**Date:** 2026-06-14

> To initialize the strategic model, first download [strategic_model_init_material.md](../strategic_model_init_material.md), open a new chat, and choose a sufficiently capable model. Good choices are GPT-5.5 Thinking with thinking effort set to Extended, GPT-5.5 Pro, Claude Opus 4.8, or Claude Sonnet 4.6. If you use Claude, set effort to High or Max and turn Thinking on. Then upload the file and start with this instruction: "Read the attached text describing the OAP concept and tell me whether you can play the role of the strategic model."

# Abstract

Orchestrated Agentic Programming is a human-governed method for building software with AI coding agents. It separates strategic reasoning from operational execution: a high-powered, long-context strategic AI helps transform domain intent into architecture, tool choices, task plans, critique, and precise work orders, while a high-autonomy execution agent works inside a hardened, rebuildable machine environment to edit code, install tools, run commands, execute tests, commit changes, and open pull requests. The human remains the control point for intent, risk, and release, but does not waste time supervising every low-level step.

This manual presents Orchestrated Agentic Programming as a practical subtype of agentic software engineering. It is more disciplined than vibe coding, more autonomous than ordinary AI pair programming, and more governable than open-ended agent swarms. Its central artifacts are a project constitution such as `AGENTS.md` for Codex CLI or `CLAUDE.md` for Claude Code CLI, narrow PR-sized work units, explicit non-goals, reproducible verification, audit-ready reports, remote-repository truth, and durable handoffs. The manual argues that the main bottleneck in AI-assisted software development is shifting from code production to validation, governance, context preservation, and judgment.

Rather than promising effortless software creation, this manual teaches a repeatable workflow for making AI-generated software auditable, constrained, test-backed, and aligned with human intent. It is a guide for freeing the human from low-level implementation labor while preserving high-level control. In OAP the human inevitably moves up the ladder: less coder, less line-level software engineer, more product owner, domain expert, engineering manager, reviewer of evidence, and release authority. The human begins by asking the strategic AI what kind of system is needed and which architecture and tools fit the domain; later the human interrogates the strategic AI for proof, risk, and readiness. The execution agent performs disposable implementation work in a bounded runtime.

# Preface

This manual is written for people who have already noticed that modern AI coding tools are no longer just autocomplete. They can inspect repositories, modify files, run tests, use terminals, and in some environments open pull requests. The practical question is no longer whether AI can produce code. The practical question is how to organize this capability so that serious software can be produced without losing control of architecture, security, correctness, documentation, and responsibility.

The method described here is called **Orchestrated Agentic Programming**, abbreviated **OAP**. The name is intentionally operational. It does not claim that every component is new. Repository instructions, coding agents, AI code review, branch-based work, human review, and multi-agent research systems all already exist [[1]](#ref-codex-agents-md); [[2]](#ref-hula); [[3]](#ref-metagpt); [[4]](#ref-chatdev). The contribution of OAP is the composition: a human lead uses a strategic model first for architecture discovery and tool selection, then for critique and work-order design, delegates implementation to a high-autonomy coding agent inside a bounded runtime, and treats every change as a reviewable, test-backed, auditable unit.

This is not a manual about asking a chatbot to write a function. It is not a manual about removing humans from software engineering. It is a manual about moving the human into a higher-leverage management role: domain expert, intent owner, product judge, risk owner, strategic interrogator, release authority, and process designer. The human should not become the agent's assistant, dependency installer, or manual traceback courier. If the workflow causes the agent to pilot the human through low-level chores, the orchestration has failed.

The manual uses examples from several project types: a public OpenAI-compatible API gateway, a private grading workflow, a public browser-based SSH workflow, and a public early-stage infrastructure management product. Private examples are used only as design material. Public sources are cited where the manual refers to broader history, tools, benchmarks, repositories, and research.

## How to read this manual

Readers who want the shortest path should read Parts I through V first, then the SLAIF API Gateway case study in Part VI. Readers building a training course should read the full document and use the appendices as workshop templates. Readers evaluating the method academically should focus on the conceptual chapters, the verification and audit chapters, the case studies, and the references.

## What this manual does not claim

This manual does not claim that OAP is a new scientific discipline. It does not claim that domain experts building or shaping software is historically new; end-user software engineering, low-code/end-user development, AI-assisted end-user coding, and citizen development all address related terrain [[5]](#ref-ko-euse-2011); [[6]](#ref-schenkenfelder-lowcode-eud-2024); [[7]](#ref-weber-ai-eud-2025); [[8]](#ref-mit-ai-citizen-dev-2024). It does not claim that coding agents are reliable enough to run without boundaries. It does not claim that high-autonomy execution is safe by default. It does not claim that a generated pull request is proof of completion. It also does not claim that the human must manually review every line of every agent-generated diff. It claims something narrower and stronger: with the right strategic control plane, project constitution, rebuildable runtime boundary, PR discipline, verification practice, and evidence interrogation, coding agents can become serious implementation labor without turning the human into their operator.
