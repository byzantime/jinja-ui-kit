# Agent notes

## Python comment and docstring rule

Python code (`src/`, `tests/`) carries no comments and keeps docstrings short, enforced by
[stifle](https://pypi.org/project/stifle/):

- No own-line comments, trailing comments or orphan string literals. Only stifle's built-in
  pragma keeps survive (`# noqa`, `# type:`, `# pragma:` etc.).
- Docstrings are at most 7 content lines; shorten longer ones by hand.
- Put rationale in names, docstrings or assertion messages instead of comments.
- Applies to Python only, not to Jinja templates, JS or CSS.

Settings live in `[tool.stifle]` in `pyproject.toml`; stifle is pinned in the `dev` dependency group.

## Commands

```sh
uv sync                              # install the package plus dev tools
uv run stifle check src tests        # lint gate
uv run stifle format src tests       # delete violating comments/orphan strings in place
uv run ruff check src tests          # ruff lint (add --fix to autofix)
uv run ruff format src tests         # ruff formatter (gate uses --check)
uv run pytest -q                     # tests
```

## Ruff

`ruff check` and `ruff format` run on `src` and `tests` with ruff's default rules; ruff is pinned in
the `dev` dependency group and configured under `[tool.ruff]` in `pyproject.toml`.

Checks run from `.sekreton/config.toml` (Sekreton gates), not a CI pipeline.
