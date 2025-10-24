# Contributing to Gnowee PSC Training Web

Thank you for your interest in contributing! This document explains how to get the project running locally, coding conventions, and the preferred workflow for changes.

## Getting started (developer setup)

1. Fork the repository and clone your fork:

```bash
git clone https://github.com/<your-username>/Gnowee-Training-PSC-Web.git
cd Gnowee-Training-PSC-Web
```

2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Run migrations and create a dev superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

5. Run the development server

```bash
python manage.py runserver
```

## Project Structure

- `psc_training_web/` - Main Django project settings and configuration
- `assessments/` - Handles assessment-related functionality
- `communication/` - Manages communication features
- `courses/` - Course management functionality
- `staffs/` - Staff member related features
- `students/` - Student management functionality
- `users/` - User authentication and authorization
- `utility/` - Common utilities and helpers

## Coding conventions

- Format Python code with Black. Line length: 88 (Black default)
- Use isort for import sorting
- Keep functions and modules small and focused
- Add or update tests for any new behavior
- Follow Django's best practices and conventions

## Branching and PR workflow

- Create a feature branch from `main` named `feature/short-description` or `fix/short-description`
- Keep commits small and focused. Rebase/squash before opening a PR if it helps readability
- Open a pull request against `main`. Fill the PR description with what changed and why
- Link relevant issue(s) and add labels if you can

## Tests & CI

- Run tests locally with:

```bash
python manage.py test
```

- Write tests for new features in the appropriate app's `tests.py`
- Run specific test cases with:

```bash
python manage.py test app_name.tests.TestCaseName
```

## Pre-commit hooks (recommended)

Install `pre-commit` and set up the hooks locally:

```bash
pip install pre-commit
pre-commit install
```

We recommend configuring hooks for:
- `black` - Code formatting
- `isort` - Import sorting
- `flake8` - Style checking

## Development Guidelines

1. **Models**
   - Keep models in each app's `models.py`
   - Use descriptive names for models and fields
   - Add docstrings explaining model purpose
   - Define `__str__` methods for all models

2. **Views**
   - Use class-based views when possible
   - Keep view logic focused and simple
   - Handle permissions explicitly
   - Document complex view logic

3. **Templates**
   - Use template inheritance
   - Keep logic out of templates
   - Use template tags for complex rendering

4. **Forms**
   - Use Django forms for all data input
   - Add proper validation
   - Include helpful error messages

## Documentation

- Add docstrings to all classes and functions
- Keep README.md updated with new features
- Document API endpoints if created
- Update CONTRIBUTING.md for workflow changes

## Reporting security issues

If you discover a security vulnerability, please contact the repository owner privately rather than opening a public issue.

## Need Help?

If you need help with:
- Setting up the development environment
- Understanding the codebase
- Making your first contribution
- Any other questions

Feel free to:
1. Check existing issues for similar questions
2. Open a new issue with the "question" label
3. Ask in pull request comments

## Thank you

We appreciate all contributions — whether it's:
- Bug fixes
- Documentation improvements
- Feature additions
- Test coverage improvements
- UI/UX enhancements