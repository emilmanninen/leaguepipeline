# Git workflow

- Commit messages use Conventional Commits with a mandatory scope: `type(scope): description`. Types: feat, fix, docs, style, refactor, perf, test, chore, build, ci. Scope names the part of the codebase affected (e.g. `frontend`, `db`, `auth`, `messages`, `ci`). Add an optional body (blank line after the subject) when the change needs context — what and why, not how. Example: `fix(messages): scroll thread to newest message on load`.
