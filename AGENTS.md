# Project Instructions

These instructions persist the workflow requested for future Codex conversations.

- Use incremental development branches named `dev_x.y.z`.
- Keep `pyproject.toml` version aligned with the active dev branch and eventual release.
- For every requested feature or fix, open a categorized GitHub issue, assign it to
  `techcioffy`, add start/end dates in the issue body or project fields, and close it
  only after the work is finished.
- Work on a dev branch, commit the feature set, push it, open a pull request into
  `main`, and let GitHub Actions run the automated tests.
- Merge to `main` only after the test suite passes. The release workflow must create
  a release only after successful tests on `main` or `master`.
- If CI fails, do not merge. Report the failing check and fix it on the dev branch.
- Keep the GitHub Project updated with planning/status/date views when permissions
  allow project automation.

