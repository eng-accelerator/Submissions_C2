# Contributing

Thank you for your interest in contributing to this repository. This project is collaborative and documentation-driven — please follow the guidelines below to keep work orderly and discoverable.

Important policy
- Only collaborators may contribute code or documentation directly to this repository. If you are not a collaborator and would like to contribute, contact the project lead (see Contact below) to request access or propose changes via an issue.
- Direct commits to the `main` or `develop` branches are strictly prohibited. All changes must go through a pull request (PR) and review process.

Branching & workflow
- Base branch for development: `develop`. Direct commits to `develop` are prohibited; use pull requests targeting `develop` for all development changes.
- Feature branches: create branches from the appropriate base branch and name them using the pattern:
  - `feat/<short-description>` for new features
  - `fix/<short-description>` for bug fixes
  - `docs/<short-description>` for documentation-only changes
- Rebase or merge the latest base branch before opening a PR to reduce merge conflicts.

Pull Requests
- Open a PR targeting the appropriate base branch (e.g., `project-setup` or a specific feature branch maintained by the team).
- PR checklist (add these to the PR description):
  - Link to an issue (if applicable).
  - Short description of the change and motivation.
  - Which template(s) were used or updated (e.g., PRD, Architecture, TDD).
  - Testing notes: which tests were added/updated and how to run them.
  - Reviewers requested (at least one maintainer or owner approval required).
- Keep PRs small and focused. Large design changes should be accompanied by documentation updates (PRD, architecture, or TDD as appropriate).

Issues & Discussions
- Use Issues to report bugs, propose features, or ask design questions. Tag issues with a concise, descriptive title and add context in the body.
- Use the `docs/project-docs/` area for project-specific documentation and proposals. For broad design discussions, open an issue or a discussion thread.

Using templates & personas
- Leverage the documentation templates under `docs/templates/` (PRD, Project Plan, Architecture, TDD) for consistent, effective project documentation.
- The `docs/ai-personas/` folder contains AI persona definitions designed to help you plan, design, and implement faster. Treat them as role-based assistants (Product Analyst, Project Manager, Solution Architect, Python AI Developer, etc.). Use the personas to draft PRDs, decompose tasks, and validate design choices.

Code style, tests & CI
- Follow the existing code style in the repository. Keep changes consistent with the project's conventions.
- Add unit tests for new logic and a single integration test for critical flows where feasible. Tests should be fast and deterministic.
- Ensure your PR passes the repository's CI checks before requesting a review. If CI is not yet configured, note tests run locally in the PR description.

Documentation updates
- All project documentation should live in `docs/project-docs/` as the project matures. Use templates from `docs/templates/` and include examples/fixtures under `docs/examples/` when helpful.

Security & sensitive data
- Do not commit secrets, credentials, or PII to the repository. Use the project's secret management approach (Vault or environment variables) and mention secret handling in your TDD if relevant.

Contact
- Project lead / maintainer: Prasanna Neelavar — prasanna.neelavar@gmail.com

License
- By contributing you agree that your contributions will be licensed under this repository's license (see `LICENSE`).

Thank you — follow the templates, use the personas, and keep contributions focused and well-documented.
