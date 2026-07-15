# SLAIF Trainings

This repository contains Markdown-first training content for SLAIF that is intended to be published under the `/trainings` site root on `edu.slaif.si`.

It is the right repository for:

- participant-facing training materials
- workshop books
- course-style instructional content
- guided learning resources that should live under `/trainings/...`

It is not the right repository for:

- platform and reference documentation that should live under `/notes/...`
- operational procedures, service workflows, and technical runbooks that should live under `/workflows/...`

## Public Publication Root

The public site root for this repository is:

- `https://edu.slaif.si/trainings`

The public page model is directory-driven:

- a directory containing `collection.md` becomes a collection page
- a directory containing `index.md` becomes a book page, unless its parent is already a book
- nested paths map to nested URLs under `/trainings/...`

In practice, this means:

- the repository root collection is published at `https://edu.slaif.si/trainings`
- a nested collection in `foo/collection.md` is published at `https://edu.slaif.si/trainings/foo`
- a book in `bar/index.md` is published at `https://edu.slaif.si/trainings/bar`
- chapter pages are published under the corresponding book path

The top-level site root is determined by the repository, not by front matter. Content created here will publish under `/trainings/...`, not under `/notes/...` or `/workflows/...`.

## Repository Structure

Important local files:

- `AGENTS.md`: repository-specific working instructions for coding tools
- `collection.md`: root collection metadata and landing-page content
- `defaults.yml`: repository defaults
- `style.css`: repository-level styling
- `.github/workflows/deploy.yml`: deploy and validation workflow wiring

When creating or updating content:

1. Work in Markdown and keep the directory structure explicit.
2. Use `collection.md` for collections and `index.md` for books.
3. Keep chapters short and scoped.
4. Treat publication as a repository workflow: branch, PR, validation, merge.
5. Keep this repository focused on `/trainings/...` content only.

## Working With Coding Tools

This repository includes a root `AGENTS.md` file to make work with coding tools more reliable and repeatable.

If you use:

- ChatGPT with the Codex option
- OpenAI Codex CLI
- Claude Code

the repository `AGENTS.md` gives the tool repository-specific instructions about:

- what belongs in this repository
- how routing and publication work
- how books and collections are structured
- how to validate and publish changes
- how to distinguish `/trainings`, `/notes`, and `/workflows`

When using coding tools here, start in the repository root so the tool can read `AGENTS.md` before making changes.

If you already have a ChatGPT subscription, check Codex access before setting up extra tooling. Codex is part of ChatGPT, and many users can enable or access it directly from their existing ChatGPT account. Codex CLI can also sign in with a ChatGPT account. In practice, that means many users can start with ChatGPT plus the repository `AGENTS.md` before deciding whether they also need CLI or IDE setup.

## Sister Repository Documentation

General documentation about the SLAIF educational content system lives in the sister repository `slaif-edu/notes` and is publicly published under `/notes`.

Useful public references:

- Notes home: `https://edu.slaif.si/notes`
- Content creation guide: `https://edu.slaif.si/notes/content-creation`
- Notes software installation: `https://edu.slaif.si/notes/software-installation`
- Codex + AGENTS.md guide (EN): `https://edu.slaif.si/notes/guide-codex-agents`
- Codex + AGENTS.md guide (SLO): `https://edu.slaif.si/notes/vodnik-codex-agents`

These pages are the right place for:

- how the content system works
- how books, collections, chapters, images, and questions are structured
- how to install and run the notes platform locally
- how to use Codex and `AGENTS.md` workflows across `slaif-edu` repositories

## SLAIF

Main public site:

- `https://www.slaif.si/`

Educational publishing root for this repository:

- `https://edu.slaif.si/trainings`
