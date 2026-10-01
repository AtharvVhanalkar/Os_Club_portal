# Contributing to the Open Source Club Portal

Thanks for contributing! This guide explains how we work. Please read it fully before claiming an issue: most questions are answered here, and maintainers will point you back to this file if you skip it.

## Ways to contribute

- Fix a bug or build a feature from the [issues](../../issues)
- Improve documentation (setup steps, screenshots, explanations)
- Report a bug you found, with steps to reproduce it
- Review someone else's pull request
- Add yourself to the Contributors Wall (a great first PR)

## Claiming an issue

1. Find an issue labelled `good first issue` if you're new, or any issue without the `assigned` label.
2. **Comment on the issue** saying you'd like to work on it, and briefly how you plan to fix it.
3. **The first person to comment gets the issue.** A maintainer will assign it to you. Please don't start work until you're assigned.
4. **One issue at a time.** Finish or unassign yourself before claiming another.
5. If you can't continue, comment so someone else can pick it up. Issues with no activity for 7 days may be reassigned.

A helpful claim comment looks like this:

> I'd like to work on this. I can reproduce it on the latest main: the seat count doesn't update after cancelling. I plan to refresh the session from the API response in `SessionDetail.jsx`.

## Your first contribution: the Contributors Wall

No issue needed. Copy `frontend/src/contributors/_template.json` to `frontend/src/contributors/<your-github-username>.json`, fill it in, and open a PR. Run `npm run check:contributors` to validate your file.

## Workflow

### 1. Set up your fork (once)

```bash
git clone https://github.com/<your-username>/oss-club-portal.git
cd oss-club-portal
git remote add upstream https://github.com/<club-org>/oss-club-portal.git
```

### 2. Start every piece of work from an updated main

```bash
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
git checkout -b fix/issue-12-seat-count
```

### 3. Branch names

`<type>/issue-<number>-<short-description>`, where type is one of `fix`, `feat`, `docs`, `test`, `chore`.

Examples: `fix/issue-12-seat-count`, `feat/issue-30-waitlist`, `docs/issue-41-windows-setup`

### 4. Commit messages

Short, in the imperative mood, with the issue number:

```
Fix seat count after cancelling registration (#12)
```

Keep each commit focused. Don't mix unrelated changes in one pull request.

### 5. Run the checks

```bash
cd backend && python manage.py test
cd frontend && npm run lint && npm run check:contributors && npm run build
```

If you change backend behavior, add or update a test in the app's `tests.py`.

### 6. Open a pull request

```bash
git push origin fix/issue-12-seat-count
```

Then open a PR from your branch to `main` on the club's repository, and:

- Fill in the pull request template
- Link the issue with `Closes #12`
- Add a screenshot or short recording for any visual change

### 7. Respond to review

Reviews are normal, not a sign you did something wrong. Push new commits to the same branch and the PR updates automatically. Reply to each comment so reviewers know it's handled. Please be patient: maintainers are students too.

## Code style

- **Python:** follow PEP 8, keep views thin and put business logic in `services.py`
- **JavaScript/React:** function components and hooks, keep API calls in `src/api/client.js`
- **CSS:** use the design tokens at the top of `global.css` rather than new hard-coded colors
- **Text in the UI:** sentence case, plain words, buttons say exactly what they do

## Using AI tools

AI assistants are welcome, with three rules:

1. **Understand every line you submit.** You should be able to explain your change in review.
2. **Don't paste AI-generated text into issues or comments** without rewriting it in your own words.
3. **Mention it in your PR** if a large part of the code was AI-generated.

PRs that are clearly unreviewed AI output will be closed.

## Never commit secrets

`.env` files, Google client secrets and tokens must never be committed. They're in `.gitignore`. If you commit one by accident, tell a maintainer immediately so the credential can be revoked.

## Questions?

Search the docs and existing issues first. If you're still stuck, ask in the club's chat channel or comment on your issue with what you tried.
