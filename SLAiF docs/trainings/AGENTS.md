# AGENTS.md

This file defines how Codex should operate in this repository when transforming seminar materials into publishable "books" for SLAIF WP6.

The purpose of this workflow is not merely to summarize source material. The goal is to convert heterogeneous inputs such as transcripts, PDFs, slide decks, notes, recordings, screenshots, and supporting documents into coherent, pedagogically sound books that fit the conventions of the content system documented in this repository.

The target platform is directory-driven and Markdown-first:

- A directory containing `collection.md` is a collection.
- A directory containing `index.md` is a book, unless its parent is already a book, in which case it is a chapter.
- Books and collections may be assembled from subdirectories or explicit front matter lists.
- Chapters are preferably short and well-scoped.
- Images, side notes, expandable images, full-width elements, code blocks, and questions are supported and should be used intentionally.
- Multilingual content should generally be represented as parallel books, not mixed-language chapters inside one book.

Codex should follow the rules below whenever asked to create, expand, revise, or validate seminar books in this repository.

## Operating Principles

Codex must optimize for these outcomes:

- Produce readable books, not raw archives of seminar material.
- Preserve factual fidelity to the source materials.
- Rewrite aggressively enough to improve clarity, structure, and pedagogy.
- Respect the repository's book and collection model.
- Keep chapter structure explicit and maintainable.
- Reuse material where appropriate, especially shared foundational chapters.
- Avoid hidden assumptions: when necessary, state inferred decisions in the generated planning notes or summaries.

Codex should treat transcripts as noisy evidence, not as publication-ready prose. Spoken structure, repetition, false starts, audience interaction, and presenter digressions should usually be normalized away unless pedagogically useful.

Codex should treat slides and PDFs as visual-semantic material, not only as text containers. Diagrams, screenshots, tables, and figures often carry core meaning and must be represented in the output.

## Default Authoring Standards

Unless the user explicitly requests otherwise, Codex should apply the following standards:

- Output language defaults to English.
- Output level defaults to `advanced`.
- Books should have a clear title, subtitle when helpful, and explicit chapter structure.
- Chapters should be short enough to read comfortably on screen.
- Subchapters should be used sparingly.
- Content should read as authored instructional material, not as a stitched compilation.
- Terminology should be normalized throughout a book.
- Important figures should be preserved or recreated as linked image assets.
- Images should have meaningful captions or surrounding explanation when they carry instructional value.
- Questions should be used when they reinforce understanding, check comprehension, or gather structured feedback.
- Existing structure should be preserved when updating a book unless there is a strong reason to reorganize it.

## Repository Model

Codex must respect the content model described in this repository:

- A top-level or nested directory may represent a collection or a book.
- A book introduction lives in the book's own `index.md`.
- Questions belong in chapters, not in the book introduction or collection description.
- Immediate chapter subdirectories containing `index.md` are gathered automatically unless front matter defines `chapters`.
- Explicit `chapters`, `books`, or `collections` lists must use the path conventions documented in this repository.
- Directory names determine order when explicit chapter lists are not present, so numeric prefixes such as `01-`, `02-`, `03-` are usually preferable.
- Shared chapters across multiple books are valid and encouraged when appropriate.

Codex must not invent unsupported content model features. If a requested structure conflicts with the documented system, Codex should choose the closest supported structure and explain that choice.

Codex should also respect these authoring details from the content system:

- Front matter is YAML enclosed between `---` lines.
- If a file needs only a title and no non-default metadata, it may begin with a single Markdown title line instead of explicit front matter.
- Book front matter may include documented keys such as `title`, `subTitle`, `public`, `language`, `coverImg`, `tocInHeader`, `quizThreshold`, `requireLogin`, `tokens`, `groups`, `admins`, and `chapters`.
- Collection front matter may include documented keys such as `title`, `subTitle`, `public`, `language`, `coverImg`, `recursiveContent`, `collections`, `books`, and `admins`.
- `recursiveContent: true` is valid only for collections and changes discovery behavior; Codex must not apply it to books.
- When using explicit lists for `chapters`, `books`, or `collections`, Codex must follow the repository path conventions exactly and must not invent new reference styles.

## Repository Identity

This repository is intended to publish to the top-level site root `/trainings` on `edu.slaif.si` once deployment is configured for this repository.

Use this repository for:

- participant-facing training materials
- workshop books
- course-style instructional content
- supporting books that are intended to live under `/trainings/...` once deployment is configured

If the user wants the final published URL to land under `/notes/...` or `/workflows/...`, Codex must say that this repository is the wrong publication target and instruct the user to switch to the corresponding repository instead of pretending that front matter or directory placement can change the top-level site root.

## SLAIF Organization Model

Codex must distinguish between:

- content-level structure inside a repository, and
- deployment-level routing across repositories in the `slaif-edu` GitHub organization

Current known top-level mappings are:

- `slaif-edu/notes` publishes under `/notes`
- `slaif-edu/workflows` publishes under `/workflows`
- `slaif-edu/trainings` publishes under `/trainings` once the deployment side is configured to accept and mount it

Rules:

- The top-level site root is determined by the repository, not by front matter.
- A book cannot be published to `/trainings/...` from inside `slaif-edu/notes`.
- A new repository alone is not sufficient to create a working new top-level site root; the deployment side must also mount or accept that repository.
- When a repository is already mounted, nested books and nested collections inside it are content-only changes and do not require server-side routing changes.

Examples:

- Creating `foo/collection.md` inside `slaif-edu/workflows` can create `/workflows/foo`.
- Creating `trainings/collection.md` inside `slaif-edu/notes` can create `/notes/trainings`, not `/trainings`.
- Creating `slaif-edu/trainings` does not by itself guarantee that `https://edu.slaif.si/trainings` is live; deployment must accept that repository.

## Repository Routing Rules

Codex must decide early whether the current repository matches the requested final URL root.

Rules:

- If the requested final URL root does not match the current repository, Codex must say so explicitly before drafting or publication work continues.
- Codex must not imply that a book can be moved between top-level roots using only front matter or directory edits.
- If the user is time-constrained and the target top-level root is not yet available, Codex may propose a fallback publication path inside an already mounted repository, such as a nested collection under `/workflows/...` or `/notes/...`.
- Codex should treat repository selection as a publication-routing concern, not as a mere organizational preference.

Default repository-selection guidance:

- `notes`: platform documentation, authoring guides, reference material
- `workflows`: operational procedures, service workflows, technical runbooks, execution guides
- `trainings`: participant-facing training materials, workshop books, course-like instructional content

## GitHub Authentication And Delegated Publication

Codex should actively help the user establish working GitHub CLI authentication when publication, repository creation, push, pull request creation, or merge delegation depends on `gh`.

Rules:

- Treat browser access to GitHub and `gh` CLI access as separate concerns.
- If `gh auth status` reports an invalid token, do not infer that the user lacks repository access; instead infer that the locally stored CLI token is stale, revoked, expired, malformed, or missing organization authorization.
- When `gh` authentication is broken, Codex should explain that repository publishing and merge delegation are blocked only at the CLI layer, not necessarily at the account or browser layer.
- When the user wants Codex to perform publication or merge steps through GitHub, Codex should prefer restoring `gh` first if that is the fastest reliable path.

### Diagnosing `gh` authentication

Codex should check:

- whether `gh auth status` succeeds
- whether the token has the scopes needed for the intended operation
- whether organization or SSO authorization is still required
- whether network restrictions in the current execution environment are making a valid token appear broken

Codex should distinguish between:

- invalid or stale token in `~/.config/gh/hosts.yml`
- valid token but missing scopes
- valid token and scopes, but blocked network path from the current session
- valid token and network, but insufficient repository or organization permissions

### Recommended token type

For terminal-only machines, Codex should recommend a classic personal access token for `gh auth login --with-token` unless there is a clear reason to use a different flow.

Recommended classic PAT scopes for delegated repository work are:

- `repo`
- `read:org`
- `gist`
- `workflow`

Rationale:

- `repo` is needed for private or internal repository access, push, branch, and pull request work
- `read:org` is needed for organization-aware operations and access checks
- `gist` is expected by GitHub CLI's documented minimum token set for `--with-token`
- `workflow` is needed if Codex must create or update files in `.github/workflows/`

Codex should explain that a token lacking `workflow` may still allow normal pushes, but GitHub may reject pushes that create or update workflow files.

### Terminal-only recovery flow

When the user is on a terminal-only machine and wants Codex to perform GitHub operations, Codex should recommend this sequence:

```bash
gh auth logout -h github.com -u <user>
gh auth login --hostname github.com --with-token
gh auth status
```

The user then pastes the newly created classic PAT when prompted.

If the user asks where to create the token, Codex should direct them to:

- `https://github.com/settings/tokens`
- `Tokens (classic)`
- `Generate new token (classic)`

with the recommended scopes above.

### Organization and SSO authorization

Codex should warn that a token may still fail even when correctly created if:

- the organization requires SSO authorization for the token
- the organization requires approval for token use
- the user lacks sufficient permissions in the target repository or organization

If the token is valid but organization access still fails, Codex should tell the user to authorize the token for the relevant organization, such as `slaif-edu`.

### When Codex may rely on `gh`

Once `gh auth status` succeeds and the environment has working network access, Codex may use `gh` for:

- repository discovery inside `slaif-edu`
- repository creation
- branch publication
- pull request creation
- workflow inspection
- deployment run inspection
- merge delegation when the user explicitly wants Codex to perform the merge and the user's permissions allow it

Codex should still prefer plain `git` where that is simpler, but when the user explicitly wants the agent to take over publication and merge operations, working `gh` access is a first-class capability and should be treated as part of task readiness.

### Reporting blocked delegation

If delegated publication or merge cannot proceed, Codex should clearly state which of the following is blocking:

- `gh` is not authenticated
- the token is missing required scopes
- the token is not authorized for the organization
- the current environment has restricted network access
- the user lacks repository or merge permissions
- deployment infrastructure accepted the repository push but rejected publication downstream

## Top-Level Roots vs Nested Collections

Codex must keep the following distinction explicit:

- A nested collection inside an already mounted repository is a content change.
- A new top-level root is a deployment change.

Consequences:

- Adding a collection under `slaif-edu/workflows` can produce URLs like `/workflows/trainings/...` without server-side changes.
- Asking for `/trainings/...` is not equivalent to asking for `/workflows/trainings/...`.
- If deployment of a new repository fails in the remote deploy step, Codex should treat this as infrastructure blocking rather than as a Markdown or content-model failure.

## Source Material Policy

Codex may receive source material in forms such as:

- diarized transcripts
- plain transcripts
- PDFs
- presentations exported as PDF or images
- slide decks in mixed formats
- markdown notes
- Word or text documents
- image folders
- links to existing books or chapters
- folders containing mixed assets

Codex should normalize all such material into a working representation before drafting or updating books.

During normalization, Codex should:

- detect source language
- detect topic boundaries
- identify repeated content across sources
- identify likely chapter candidates
- identify diagrams, screenshots, tables, and workflows that need visual retention
- separate metadata, logistics, and audience interaction from the core instructional content
- preserve provenance when useful for later review

## Book Quality Requirements

A viable WP6 book should satisfy all of the following:

- It has a stable directory structure.
- It has valid front matter or a valid title line.
- It is internally coherent and readable without attending the original seminar.
- It is written for the configured audience level.
- It uses consistent terminology in the configured output language.
- It contains appropriately scoped chapters.
- It integrates relevant images, diagrams, screenshots, or other visual evidence when these carry meaning.
- It distinguishes core content from side notes, examples, and optional detail.
- It contains questions only where they add value and where the format is valid for this platform.
- It can be validated structurally before publication.

## Command Interface

The following commands define the expected operational behavior of Codex in this repository.

Commands are written here in a human-facing form. Exact shell syntax is not required; these are agent instructions and workflow triggers.

The command names in this section are a workflow interface for the agent, not a guarantee that the repository ships shell executables with the same names.

Interpretation rules:

- `set language` and `set level` are conversational agent directives, not literal shell commands.
- `check-tools` is an agent task that typically probes local binaries and capabilities.
- `ingest`, `plan-book`, `draft-book`, `update-book`, `quizify`, `sidenotify`, `align-editions`, and `publish-book` are agent workflow phases. They may involve multiple concrete tools or direct file edits.
- `lint-book` is a required validation behavior, not automatically a literal local executable. If the repository does not provide a concrete `lint-book` command, Codex must run the closest real validation path available, name it explicitly, and report its limitations.
- Codex must not pretend that a workflow label from this section is a shipped CLI command unless it has verified that such a command actually exists in the current environment.

### `help`

List all supported commands with a one-line explanation and minimal usage form.

Use this when the user asks what Codex can do in this repository.

Output format rules:

- Present the command list in a short table-like form that is easy to scan.
- Each row should include the command and a concise explanation.
- Keep the output compact; `help` is an index, not full documentation.

### `help <command>`

Explain one specific command in more detail.

The explanation should include:

- purpose
- expected inputs
- output artifacts
- important defaults
- common edge cases
- whether the command creates new content, modifies existing content, or only validates

### `set language <language>`

Set the output language for all subsequent planning, drafting, translation, image-caption writing, quiz writing, and metadata generation.

Rules:

- This affects output, not interpretation. Sources may remain multilingual.
- The agent should still read all source languages it can understand, but must produce the final material in the configured language unless explicitly told to preserve multilingual fragments.
- If the user later calls `align-editions`, the current language setting applies to the target edition being created or maintained.

Expected effects:

- prose language
- chapter titles
- captions
- summaries
- quiz text
- front matter `language` where applicable

### `set level <beginner|advanced|expert>`

Set the intended expertise level of the target readership.

Rules:

- `beginner`: explain terms early, reduce assumed prior knowledge, use more examples, shorter conceptual jumps, more explicit signposting.
- `advanced`: assume domain familiarity, but still explain non-obvious concepts and decisions.
- `expert`: compress basic exposition, focus on precision, nuance, methodology, and edge cases.

This setting applies to:

- chapter pacing
- terminology density
- example depth
- amount of scaffolding
- quiz difficulty
- whether side notes should hold advanced detail or be omitted

### `ingest <sources>`

Normalize source materials into a structured working corpus.

This command does not directly create the final book unless explicitly combined with drafting. Its purpose is to make all sources machine-usable and reviewable.

Expected behaviors by source type:

- For transcripts: extract thematic blocks, normalize speaker noise, preserve timestamps when useful, and identify instructional sections versus logistics or discussion noise.
- For PDFs and slide decks: inspect each page visually, extract text, capture page structure, detect figures and diagrams, and preserve meaningful page-to-asset relationships.
- For image-heavy documents: identify images that should become standalone assets and note their likely role in the final book.
- For mixed folders: inventory files, cluster them by topic and format, and identify duplicates or overlapping versions.

Expected output of ingestion:

- a normalized markdown representation of sources
- extracted or linked visual assets when useful
- a source inventory
- topic segmentation
- notes about quality issues, missing pages, unreadable scans, or language mismatches

If source ingestion reveals conflicting versions of the same material, Codex should preserve the conflict for later resolution rather than silently choosing a winner unless one version is clearly newer or more complete.

### `check-tools`

Inspect whether the local environment contains the external tools needed for realistic ingestion and conversion work.

This command should check for capabilities such as:

- PDF page rasterization and inspection
- image conversion and cropping
- OCR for scanned documents when needed
- reading or converting Microsoft Office formats
- reading or converting OpenDocument formats
- archive unpacking

Typical useful tools include:

- `pdftoppm`
- `pdftocairo`
- `pdfinfo`
- `mutool`
- `magick` or `convert`
- `ffmpeg`
- `libreoffice` or `soffice`
- `unoconv`
- `pandoc`
- `tesseract`
- `file`
- `unzip`

Rules:

- Report tools by capability, not only as a flat list of binaries.
- Distinguish between required tools for the current task and optional tools that are merely helpful.
- If multiple tools can satisfy the same capability, say so.
- If important tools are missing, explain what they are needed for and how the user can install them.
- Installation guidance should be pragmatic and, when possible, appropriate to the current environment.

This command should normally be run before heavy ingestion work on PDFs, slide decks, office files, scans, or mixed source bundles.

Unless the repository provides a literal `check-tools` executable, Codex should treat this as an agent task and report the actual probing steps it performed.

### `plan-book <target-path> [from <sources>]`

Design the structure of a new book before drafting content.

This command should produce a planning artifact or planning summary that covers:

- proposed book title
- optional subtitle
- target language
- target level
- proposed directory layout
- chapter list and ordering
- whether chapters should be directory-based or explicitly listed in front matter
- candidate shared chapters
- visual asset strategy
- quiz strategy, if applicable
- open editorial decisions or ambiguities

Planning rules:

- Prefer short, well-scoped chapters.
- Avoid overfitting the book structure to seminar chronology.
- Reorganize around concepts, workflows, or learning progression when that improves readability.
- Distinguish book-introduction content from chapter content.
- When the material naturally belongs in several books or a collection, say so.

This command is required before substantial drafting when the structure is unclear.

### `draft-book <target-path> [chapters <spec>]`

Generate the actual book and chapter markdown for a new book.

This command should:

- create or update `index.md` for the book
- create chapter directories and chapter `index.md` files as needed
- write front matter when needed
- write coherent prose based on ingested materials
- integrate visual references and extracted images
- use platform components only where they improve the reading experience

Authoring rules:

- Do not preserve transcript form unless explicitly requested.
- Convert spoken explanation into authored prose.
- Remove repetitions, filler, and presentational artifacts.
- Keep examples that materially help learning.
- Use `Sidenote`, `FullWidth`, `ExpandingSideImg`, or other supported components only when their role is clear.
- Use supported front matter keys only; if only the title is needed, a plain `# Title` opening is acceptable.
- Use explicit `chapters` front matter if chapter reuse or non-local chapter composition is required.
- If the material suggests a collection rather than a single book, stop and recommend `plan-book` for a collection-aware structure.

When drafting from multilingual sources, Codex should unify terminology in the configured output language and avoid leaking source-language fragments unless they are cited intentionally.

### `update-book <target-path> from <new-sources>`

Add new material to an existing book conservatively.

This command is distinct from `draft-book`. It should preserve the existing book's structure, identifiers, and intent whenever possible.

Expected behavior:

- ingest the new material
- compare it against the existing book and chapter structure
- determine whether the new material belongs in:
  - an existing chapter
  - a new section within an existing chapter
  - a new chapter
  - an appendix or supplementary note
  - a separate sibling book
- produce or follow a merge plan
- revise only the necessary files

Conservative update rules:

- Preserve stable chapter ordering unless there is a strong reason to change it.
- Preserve question IDs where continuity matters.
- Preserve links and shared chapter references where possible.
- Do not rewrite unrelated chapters just to normalize style unless explicitly requested.
- If the new material substantially changes the conceptual structure, propose a controlled re-plan before editing.

Use this command when seminar follow-up material, revised slides, corrections, or supplemental notes need to be incorporated into a book that already exists.

### `quizify <target-path> [scope <chapter|book>] [density <low|medium|high>]`

Add or propose questions compliant with the documented `<Question>` format.

This command should decide whether questions are used for:

- reinforcement during reading
- comprehension checking
- graded assessment
- feedback collection
- file upload assignments

Rules:

- Questions must be placed in chapters, not in book introductions or collection descriptions.
- Every question must have a stable ID when duplication or later editing could matter.
- Questions without scoring logic must be explicitly marked `ungraded`.
- Explanations should be used when they improve learning, especially for conceptual questions.
- Attempts and point values should match the pedagogical intent.

Density guidance:

- `low`: questions only at high-value moments
- `medium`: one or more questions in most important chapters
- `high`: regular reinforcement throughout the book

Codex should prefer fewer good questions over many weak ones.

### `sidenotify <target-path> [scope <chapter|book>] [density <low|medium|high>]`

Add or propose side notes using the supported `<Sidenote>` component.

This command should decide where side notes genuinely improve readability, orientation, and pedagogy without turning the page into a collection of decorative asides.

Side notes are especially useful for:

- brief definitions or terminology clarifications
- warnings about common mistakes
- short contextual remarks that would otherwise interrupt the main flow
- compact examples that support, but do not carry, the main argument
- editorial orientation for complex passages

Rules:

- Side notes must support the main text, not replace it.
- Do not move essential explanations into a side note if the chapter would become unclear without it.
- Prefer short side notes over long multi-paragraph digressions.
- Use the documented `<Sidenote>` component rather than obsolete styling tricks unless there is a clear reason not to.
- Avoid placing multiple long side notes too close together.
- Do not repeat a paragraph from the main text in slightly different words just to fill the margin.
- Prefer adding side notes in chapters; use them in a book introduction only when they materially improve orientation.

Density guidance:

- `low`: add side notes only at the highest-value moments
- `medium`: add side notes in most substantial chapters where they clearly help
- `high`: use side notes regularly, but still selectively and with restraint

Expected output:

- inserted `<Sidenote>` blocks, or
- a proposal describing where they should be inserted and why

### `align-editions <source-book> <target-book> [language <lang>]`

Create or maintain a parallel edition of a book in another language.

This command should follow the repository's preferred multilingual pattern: separate but aligned books, not mixed-language chapters inside a single book.

Expected behavior:

- mirror structure between the source and target books
- preserve chapter correspondence
- preserve the role of figures, examples, and questions
- translate and adapt content to the target language and configured level
- keep cross-edition links or references when useful

Rules:

- Do not assume exact sentence-by-sentence translation is ideal.
- Adapt for readability in the target language while preserving content and structure.
- Preserve quiz intent even when phrasing changes.
- If the source and target books have drifted structurally, propose a reconciliation plan before applying broad edits.

### `lint-book <target-path> [strict]`

Validate a book structurally and editorially.

Technical checks should include:

- valid front matter
- required title presence
- valid chapter references
- missing or broken local paths
- broken internal links
- malformed component usage
- invalid or suspicious image references
- duplicate or unstable question IDs
- unsupported question combinations
- misplaced questions outside chapters

`strict` mode should additionally check:

- chapter length and scope
- excessive nesting
- terminology inconsistency
- abrupt language switching
- poor visual integration
- likely transcript artifacts left in place
- weak pedagogical ordering
- missing explanatory bridges between sections

The output should be a concise report with:

- errors that must be fixed
- warnings that should be reviewed
- optional improvement suggestions

If the repository does not provide a literal `lint-book` command, Codex must:

- identify the concrete validation path it is using instead
- explain why that path is the closest equivalent
- state any remaining gaps between the ideal `lint-book` behavior and the concrete checks that were actually run

### `publish-book <target-path> [to <repo>]`

Prepare a finished book for submission into the publication repository.

This command is for the final submission step after drafting, updating, quiz authoring, and validation are complete. It should do as much as possible with plain `git`, without assuming that `gh` or any other GitHub CLI tooling is available.

This command publishes only within the current repository's mounted site root. It does not create or activate a new top-level root on `edu.slaif.si`.

Default assumptions:

- the default target repository is `https://github.com/slaif-edu/trainings`
- the target organization is `slaif-edu`
- the user must already have access to that organization or have accepted an invitation to it
- `git` is available locally
- the supported publication workflow is a branch in the target repository itself, pushed to `origin`
- fork-based pull request workflows are not supported and must never be suggested
- opening the actual pull request in the browser is a normal manual step unless the user explicitly provides other tooling
- merging the pull request is also a normal manual step unless the user explicitly wants Codex to do it through `gh` and the user's permissions allow it

GitHub check semantics for this repository:

- `Test deployment` is the required gate for merge. If it fails, the PR must not be merged.
- `Deployment warnings` is informative even if GitHub renders it as a red failed check. It warns about risky consequences such as deleting books that contained questions, but it does not by itself forbid merge.
- `Broken links` does not run before merge in the normal PR phase; it runs only during the merge/deploy path because it depends on the merged site state.

Expected behavior:

- verify that `lint-book <target-path> strict` has succeeded, or run the equivalent validation before proceeding
- verify that the target book is structurally complete and that required assets, chapter files, and local links are present
- verify that the current repository is the correct publication target for the desired top-level URL root
- determine whether the current working tree is already the target repository or whether the book still needs to be copied into `slaif-edu/trainings`
- if the book is not yet in the target repository, prepare a clear transfer plan rather than pretending submission is complete
- inspect `git status` and identify whether unrelated changes in the worktree would interfere with a clean submission
- create a dedicated branch name proposal for the submission
- stage the relevant files when it is safe to do so
- prepare a commit message proposal and, if the user wants, create the commit
- prepare a pull request title and body
- when the user has access to `slaif-edu/trainings`, prepare the workflow as a same-repository branch on `origin`
- provide the exact `git push -u origin <branch>` command needed to publish the branch
- provide the repository URL where the user should open the pull request manually
- explain whether the current PR is blocked by `Test deployment` or only carries informational `Deployment warnings`
- treat `git push` as an intermediate transport step, not as completion of publication
- explain that the normal publication checkpoint is an open pull request with checks running, while the server update is triggered only after merge

Expected output artifacts:

- a submission readiness summary
- a list of files that belong in the submission
- a proposed branch name
- a proposed commit message
- a proposed pull request title and body
- the exact next manual steps required from the user

Submission rules:

- do not assume that opening a pull request can be automated
- do not require `gh`
- do not push or open a pull request unless the user explicitly asks for that and the environment supports it
- do not treat a bare branch push without a pull request as a successful publication outcome
- do not stop after push if the user's goal is publication; publication remains incomplete until the pull request exists, checks run, and merge occurs
- do not treat `Deployment warnings` alone as a hard publication blocker in this repository; explain the warning and the consequence, then distinguish it from a failed required check
- do not imply that merging a PR in this repository can create a new top-level site root such as `/trainings` if that root is not already mounted by deployment
- if unrelated local changes would make staging ambiguous, stop and explain how to isolate the book changes cleanly
- if the current repository is not `slaif-edu/trainings`, say so explicitly and prepare the book for transfer instead of implying that publication is already wired up
- never suggest creating or using a fork for publication
- if the user lacks access to `slaif-edu`, state that publication is blocked until access is granted
- if the user has access, prefer and describe only the same-repository branch workflow through `origin`
- treat merge into the default branch as the step that leads to publication; do not claim the book is published merely because the local files are ready

Additional routing rules:

- In `slaif-edu/notes`, successful publication leads to URLs under `/notes/...`.
- In `slaif-edu/workflows`, successful publication leads to URLs under `/workflows/...`.
- In `slaif-edu/trainings`, successful publication is expected to lead to URLs under `/trainings/...` only if the deployment side has already been configured to accept that repository.
- If deployment is triggered automatically but fails in a remote SSH deploy step, Codex should report that repository-level CI exists but infrastructure acceptance is still blocking publication.
- A pushed branch without a pull request is an incomplete state: validation may be absent or detached from review, and the documented server update does not happen from push alone.
- An open pull request is the normal state that triggers validation; merge is the step after which the server-side update is expected to run.
- In this repository's PR UI, GitHub may show `Deployment warnings` as a red failure even though it is informational. Codex must distinguish that from a failed required gate such as `Test deployment`.
- Because `Broken links` runs only on the merge/deploy path, Codex must not claim that the absence of a pre-merge broken-links check means links were validated.

This command modifies publication metadata or git state only when needed for submission. It should not rewrite the book's prose unless submission checks reveal problems that must be fixed first.

### Recommended Workflow

For a new book:

1. `set language <language>`
2. `set level <beginner|advanced|expert>`
3. `check-tools`
4. `ingest <sources>`
5. `plan-book <target-path>`
6. `draft-book <target-path>`
7. `quizify <target-path>` if needed
8. `sidenotify <target-path>` if helpful
9. `lint-book <target-path> strict`
10. `publish-book <target-path>`

For extending an existing book:

1. `set language <language>` if changing or confirming output language
2. `set level <level>` if changing or confirming target readership
3. `check-tools`
4. `ingest <new-sources>`
5. `update-book <target-path> from <new-sources>`
6. `quizify <target-path>` if the new content warrants questions
7. `sidenotify <target-path>` if helpful
8. `lint-book <target-path> strict`
9. `publish-book <target-path>`

For multilingual expansion:

1. `set language <target-language>`
2. `set level <level>`
3. `align-editions <source-book> <target-book> [language <target-language>]`
4. `sidenotify <target-book>` if helpful
5. `lint-book <target-book> strict`
6. `publish-book <target-book>`

## Writing Rules for Codex

When writing books, Codex should:

- prefer clean authored prose over raw source order
- preserve core definitions, procedures, and conclusions from the sources
- identify and eliminate filler or duplicate explanation
- convert spoken demonstrations into readable step-by-step exposition
- make implicit transitions explicit
- keep the reader oriented with headings and local summaries where useful
- use examples where they materially aid comprehension

Codex should not:

- dump raw transcript blocks as final content unless explicitly requested
- invent facts not supported by the source material
- flatten important diagrams or screenshots into vague prose if the visual matters
- create unsupported front matter keys or custom components not documented here
- place questions in invalid locations
- over-style content when plain Markdown would be clearer

## Tool Availability and Missing Dependency Rules

Codex should actively assess whether the local environment contains the tools required by the current task.

Before source-heavy work, especially when dealing with PDFs, office files, scans, images, or archives, Codex should either run `check-tools` explicitly or perform the equivalent reasoning internally.

If a required tool is missing, Codex should:

- state which capability is blocked
- name the missing tool or a small set of acceptable alternatives
- explain why the tool is needed for the requested work
- provide concise installation guidance when possible
- continue with any partial work that remains possible without that tool

Examples:

- If PDF pages need to be rendered to images and no suitable converter is available, explain that a tool such as `pdftoppm`, `pdftocairo`, `mutool`, or an ImageMagick-backed converter is needed.
- If Word, PowerPoint, or spreadsheet files need conversion and no suitable reader is available, explain that `libreoffice` or `soffice` is typically the most useful fallback.
- If scanned pages require OCR and no OCR engine is available, explain that `tesseract` or an equivalent OCR tool is needed.
- If image extraction or cropping is required and no image-processing utility is available, explain that ImageMagick or another image tool is needed.

Codex should not fail silently when conversion or extraction is blocked by missing tooling.

## Image and Media Rules

When source materials include meaningful visuals, Codex should preserve them intentionally.

Preferred handling:

- Use ordinary Markdown images for ordinary illustrative content.
- Use `ExpandingSideImg` when a compact inline visual should expand for closer inspection.
- Use `FullWidth` when the visual genuinely needs more width.
- Use `ReplayImg` or animated image patterns only when motion explains a process.
- Use YouTube embedding only when the video itself is part of the instructional material.

Additional platform rules:

- Image paths are relative to the current Markdown file unless an intentional web URL is used.
- `ExpandingSideImg` may include a `caption` and explanatory body content; use it when the explanation needs to travel with the image.
- `ReplayImg` is preferable for one-shot animations that need an explicit replay affordance.
- `FullWidth` is appropriate for images, videos, or other wide elements that would otherwise be cramped in normal chapter width.
- If animated imagery is pedagogically useful, Codex may reference or generate `.png`/APNG or GIF assets, but only when motion materially improves understanding.

If a PDF page contains both text and a central diagram, Codex should avoid losing that diagram during extraction. The final chapter should either include the extracted diagram directly or explain why it was omitted.

All important images should have enough surrounding context that a reader understands why the image is there.

Codex should avoid decorative media insertion. If an image, animation, or video does not improve comprehension, plain prose is preferable.

## Question Authoring Rules

Questions are optional but valuable. When using them, Codex must respect the documented format.

Codex should choose question types intentionally:

- multiple choice for factual or conceptual discrimination
- short text for brief recall or terminology
- long text for reflection or open response
- upload or uploads for assignment-style tasks

Codex should also decide whether the question is:

- graded
- ungraded
- explanatory
- diagnostic
- summative

Explanations should be included when they improve learning, especially where misconceptions are likely.

Platform-specific rules:

- Questions can only appear in chapters, never in a book introduction or collection description.
- Every question needs a stable ID. If `id` is omitted, the question text becomes the ID, so text changes can break continuity of stored answers.
- Use explicit `id` values whenever the same question text may recur or when a published question may later be reworded.
- Multiple-choice questions use `options`; the correct option may be marked with `*`, or correctness may be defined via `answer`.
- Short-text questions may use `answer`, `checker`, and `scorer` as needed.
- Long-text questions typically use `longtext` and are usually `ungraded` unless there is a very clear scoring model.
- Upload questions use `upload` or `uploads`; such questions must not define `answer` or `scorer`.
- Questions without scoring logic must be explicitly marked `ungraded`.
- `attempts` and `points` should reflect actual pedagogical intent rather than defaults by accident.
- Explanations belong inside the `<Question>` block as `<Explanation>` children and may intentionally appear after an attempt or after a correct answer.

Codex must be conservative with advanced question logic. If `checker` or `scorer` functions are used, they should be simple, readable, and clearly justified by the teaching goal.

Codex must avoid unstable question behavior, including:

- duplicate IDs within a book
- upload questions combined with automatic scoring
- open-ended questions that are accidentally left graded without a coherent scoring rule
- silently changing the effective ID of an already published question

## Layout and Styling Rules

Codex may use supported layout components, but should strongly prefer the modern documented ones over older styling tricks.

Preferred components:

- `<Sidenote>` for compact supporting content in the side column
- `<FullWidth>` for wide media or other broad elements
- `<ExpandingSideImg>` for compact expandable images with captions or associated explanation
- `<ReplayImg>` for one-shot animated images
- `<YouTube>` only when the embedded video is itself part of the instruction

Code block rules:

- Use fenced code blocks with a language identifier whenever possible.
- The platform uses Expressive Code, so language tags should be real supported language identifiers.
- Collapse options or similar Expressive Code features should only be used when they materially improve readability.

Styling constraints:

- Most legacy styling based on `<!!! ... !!!>` blocks is obsolete.
- Prefer `<Sidenote>` over `float-aside` for anything more than a very short paragraph or a simple image.
- Use `retina` only when a double-resolution image actually needs size correction.
- Use `float-aside` only sparingly for short simple material when a full component would be excessive.
- Do not rely on undocumented or ad hoc styling markup.

## Multilingual Rules

The repository guidance and seminar transcript suggest that multilingual support should usually be implemented through separate books with aligned structure.

Therefore:

- Do not mix languages chapter-by-chapter inside one book unless the user explicitly requests it.
- Prefer parallel books with matching chapter layout.
- When useful, add references or links between language editions in the book introduction.
- Preserve structural correspondence to make future updates manageable.

## Update and Merge Rules

When adding new material to an existing book, Codex should first determine whether the new material:

- extends an existing concept already covered
- refines or corrects existing text
- introduces a genuinely new topic
- belongs better as an appendix or resource section
- warrants a sibling book rather than continued growth of the current one

If the new material overlaps partially with existing material, Codex should merge for clarity rather than append redundant sections.

If the new material conflicts with existing content, Codex should:

- prefer the newer or more authoritative source when that is clear
- otherwise preserve the conflict as an issue for editorial review

## Validation Before Completion

Before considering a book task complete, Codex should ensure that:

- all created or modified markdown files are structurally valid
- directory naming and chapter references are consistent
- image references point to real assets
- questions, if present, follow the documented schema
- the final result matches the configured language and level
- the book is readable as a standalone artifact

If the task includes publication or submission, Codex should also ensure that:

- the target repository for submission is explicit, with `https://github.com/slaif-edu/trainings` as the default unless the user overrides it
- the book is either already located in that repository or accompanied by a concrete transfer plan
- the relevant files for submission are identified
- the git branch, commit message, exact `git push -u origin <branch>` command, and pull request draft are prepared as far as the environment allows
- the workflow assumes direct push access to the target repository and does not propose forks
- any missing repository access, unclear remote configuration, or blocked manual step is stated explicitly

If any important uncertainty remains, Codex should say what is uncertain and where in the output that uncertainty affects content.

## What Success Looks Like

A successful Codex run in this repository produces books that:

- are faithful to seminar material
- are substantially better organized than the raw sources
- fit the documented collection and book system
- are visually and pedagogically usable
- can be validated before publication
- can be extended later without structural chaos

That is the standard Codex should aim for in all book-generation work for SLAIF WP6.
