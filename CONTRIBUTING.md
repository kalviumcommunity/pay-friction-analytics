# Team Workflow Guide

This repository uses a lightweight GitHub-based workflow so multiple teammates can work safely on the same codebase without breaking the main branch.

## 1. Branching strategy

- Keep the main branch releasable at all times.
- Create a short-lived branch for every task.
- Start each branch from the latest main branch.
- Use a consistent naming convention:
  - feature/123-short-description
  - fix/123-short-description
  - docs/123-short-description
  - chore/123-short-description

Example:

```bash
git checkout main
git pull origin main
git checkout -b feature/123-churn-model
```

## 2. Issues before code

Every change should begin with a GitHub issue.

An issue should include:
- a clear title
- a short description of the problem or request
- acceptance criteria
- labels such as feature, bug, docs, or high-priority
- one assignee

Do not start implementation until the issue exists and is linked to the work.

## 3. Pull requests and review

When a branch is ready:
1. Push the branch to GitHub.
2. Open a pull request.
3. Link the related issue in the PR description using "Closes #123".
4. Request review from at least one teammate.
5. Address review feedback.
6. Merge only after approval.

A pull request is the quality gate for the repository.

## 4. Commit message conventions

Use conventional commits so the change history is readable and machine-friendly.

Format:

```text
type: short summary

optional body
```

Common types:
- feat: a new feature or capability
- fix: a bug fix or correction
- docs: documentation-only changes
- refactor: code cleanup without behavior change
- test: tests or validation changes
- chore: maintenance tasks

Examples:
- feat: add churn model training pipeline
- fix: correct null handling in data profiler
- docs: update onboarding steps for analysts
- refactor: extract shared preprocessing logic

## 5. Review expectations

A good pull request should:
- explain what changed and why
- include the related issue number
- keep the scope focused
- include testing or validation notes when relevant

## 6. Recommended team rhythm

- Create an issue before coding.
- Work on a dedicated branch.
- Keep commits small and meaningful.
- Open a pull request early for feedback.
- Merge only after review and validation.
