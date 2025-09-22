# Contributing to NodeBox

Hi there! Thanks for considering contributing to **NodeBox**.
We welcome all contributions, big or small – from fixing typos to adding new features.

---

## Getting Started

1. **Fork the Repository**
   - Click the **Fork** button on the top right of this repo.

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/shreyansh-shankar/Nodebox.git
   cd Nodebox
   ```

3. **Create a Branch**
    ```bash
    git checkout -b origin/main
    ```

4. **Install Dependencies**
    We use Python with the following requirements:
    ```bash
    pip install -r requirements.txt
    ```

5. **Set up Pre-commit Hooks**
    We use pre-commit hooks to ensure code quality and consistency. After installing the requirements, set up the hooks:
    ```bash
    pre-commit install
    ```
    This will automatically run several code quality checks before each commit.

## Development Workflow
- Keep your code clean, modular, and well-documented.
- Test before submitting a PR.
- Use clear commit messages (e.g., fix: corrected typo in docs or feat: added workflow export option).
- All code changes will automatically be checked by our pre-commit hooks for formatting and code quality.

## Pre-commit Hooks

We use pre-commit hooks to ensure code quality and consistency across the project. These hooks automatically run before each commit to check and format your code according to our standards.

### What the hooks do:
- Remove trailing whitespace
- Fix end of file markers
- Check YAML files for syntax errors
- Check for large files that shouldn't be committed
- Check Python AST (Abstract Syntax Tree)
- Remove debug statements
- Format code with Black
- Sort imports with isort
- Remove unused imports and variables with autoflake
- Lint code with Ruff
- Format code with Ruff
- Check code style with flake8
- Security linting with Bandit

### Running pre-commit hooks manually
You can run the hooks on all files manually with:
```bash
pre-commit run --all-files
```

If any hooks fail, they will either automatically fix the issue (like formatting) or show you what needs to be fixed. After fixing, you'll need to stage the changes and commit again.

### Skipping pre-commit hooks
In rare cases, you might need to skip the hooks (e.g., for WIP commits):
```bash
git commit --no-verify -m "Your message"
```
However, this should be avoided when possible, especially for final commits.

## Guidelines for Contributions
- Issues: Pick an issue labeled hacktoberfest or good first issue if you are new.
- Pull Requests:
    - PRs should be small and focused.
    - Reference the issue number (e.g., Fixes #12).
    - Add screenshots/gifs if you change the UI.

## Code of Conduct
By participating in this project, you agree to uphold our Code of Conduct
Please be respectful and constructive in all discussions.

## Hacktoberfest Notice
This repository has the hacktoberfest topic, so your contributions will count!
- Issues labeled hacktoberfest are great starting points.
- Maintainers will mark valid PRs with the hacktoberfest-accepted label.

## Need Help?
If you get stuck:
- Check the [Docs](https://nodeboxlab.web.app/docs.html)
- Open a Discussion on our [Discord](https://discord.gg/8gg5kdpr)
- Or ask in our community [Discord](https://discord.gg/8gg5kdpr)

### Every contribution matters – thank you for helping make NodeBox better!
