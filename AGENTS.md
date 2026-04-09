# AGENTS.md

## Current Reality

- This repo is still documentation-first. `README.md` explicitly says the application code does not exist yet; do not assume Django, React, tests, or build tooling are already scaffolded.
- Treat `README.md` and `PRD.md` as the current source of truth for product scope and intended stack. If either conflicts with future code or config, prefer the executable source.

## What Exists Today

- Root files are minimal: `README.md`, `PRD.md`, `LICENSE`, and `skills-lock.json`.
- The only shipped implementation artifacts are bundled agent skills under `.agents/skills/` and `.claude/skills/`.
- `skills-lock.json` currently pins only one installed skill: `skill-creator`.

## Working In This Repo

- Before proposing implementation changes, verify whether the requested file or stack setup actually exists. In this repo, that is easy to guess wrong.
- Do not invent project commands. There is currently no verified `package.json`, Python dependency manifest, CI workflow, lint config, test runner config, or `opencode.json` in the repo root.
- If asked to implement the app, expect to create the initial project structure from scratch rather than modifying an existing Django/React codebase.

## High-Value References

- `README.md`: repo purpose, current status, intended stack, and why `AGENTS.md` exists here.
- `PRD.md`: functional scope, target API surface, data model, business rules, and still-pending technical decisions.
- `.agents/skills/skill-creator/SKILL.md`: concrete workflow for creating or improving repo-local skills.

## Repo-Specific Cautions

- The intended backend/frontend stack in docs is Django + React, but this is a target architecture, not a verified implementation.
- `PRD.md` defines target endpoints such as `POST /api/tasks/parse/` and `POST /api/tasks/ask/`; treat them as planned contracts until code exists.
- Because the repo is course material, keep changes explicit and instructional. Avoid adding speculative architecture notes to this file unless they are backed by repo content.
