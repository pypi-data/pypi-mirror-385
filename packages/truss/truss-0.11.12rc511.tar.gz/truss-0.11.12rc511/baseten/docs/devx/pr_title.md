# Pull Request Title Convention

Pull requests must follow the format from [conventionalcommits](https://www.conventionalcommits.org):
```
type(scope): Message
```

Example:
```
fix(django,mcm): Fix the networking bug
```

## Types
- `fix`: Bug fixes and patches
- `feat`: New features and enhancements
- `refactor`: Refactoring and code cleanup
- `misc`: Other changes like docs, etc.

## Scopes
The list of allowed scopes can be found in `bin/ci/pr_title_check.js`. If you need to add a new scope, please update this file.

## Format Check
A GitHub Action will validate your PR title and comment if it doesn't match the expected format. The check runs when PRs are opened or edited.
