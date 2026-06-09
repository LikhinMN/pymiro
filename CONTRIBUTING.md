# Contributing to pymiro

## Setup
git clone https://github.com/LikhinMN/pymiro
cd pymiro
uv sync

## Running tests
uv run pytest tests/ -v

## Code style
uv run ruff check .
uv run mypy pymiro/ --strict

## Branching strategy
feat/* → dev → main

## Pull request checklist
- [ ] Tests added for new behavior
- [ ] mypy passes --strict
- [ ] ruff passes clean
- [ ] CHANGELOG updated
