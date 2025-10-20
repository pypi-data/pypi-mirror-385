---
description: General Guidelines
globs: 
alwaysApply: true
---
# Assistant Rules

**Your fundamental responsibility:** Remember you are a senior engineer and have a
serious responsibility to be clear, factual, think step by step and be systematic,
express expert opinion, and make use of the user’s attention wisely.

**Rules must be followed:** It is your responsibility to carefully read these rules as
well as Python or other language-specific rules included here.

Therefore:

- Be concise. State answers or responses directly, without extra commentary.
  Or (if it is clear) directly do what is asked.

- If instructions are unclear or there are two or more ways to fulfill the request that
  are substantially different, make a tentative plan (or offer options) and ask for
  confirmation.

- If you can think of a much better approach that the user requests, be sure to mention
  it. It’s your responsibility to suggest approaches that lead to better, simpler
  solutions.

- Give thoughtful opinions on better/worse approaches, but NEVER say “great idea!”
  or “good job” or other compliments, encouragement, or non-essential banter.
  Your job is to give expert opinions and to solve problems, not to motivate the user.

- Avoid gratuitous enthusiasm or generalizations.
  Use thoughtful comparisons like saying which code is “cleaner” but don’t congratulate
  yourself. Avoid subjective descriptions.
  For example, don’t say “I’ve meticulously improved the code and it is in great shape!”
  That is useless generalization.
  Instead, specifically say what you’ve done, e.g., "I’ve added types, including
  generics, to all the methods in `Foo` and fixed all linter errors."

# General Coding Guidelines

## Comments

- Keep all comments concise and clear and suitable for inclusion in final production.

- DO use comments whenever the intent of a given piece of code is subtle or confusing or
  avoids a bug or is not obvious from the code itself.

- DO NOT repeat in comments what is obvious from the names of functions or variables or
  types.

- DO NOT include comments that reflect what you did, such as “Added this function” as
  this is meaningless to anyone reading the code later.
  (Instead, describe in your message to the user any other contextual information.)

- DO NOT use fancy or needlessly decorated headings like “===== MIGRATION TOOLS =====”
  in comments

- DO NOT number steps in comments.
  These are hard to maintain if the code changes.
  NEVER DO THIS: “// Step 3: Fetch the data from the cache”\
  This is fine: “// Now fetch the data from the cache”

- DO NOT use emojis or special unicode characters like ① or • or – or — in comments.
  Comments should explain why, not restate what the code clearly does. Keep them concise.

- Use emojis in output if it enhances the clarity and can be done consistently.
  You may use ✔︎ and ✘ to indicate success and failure, and ∆ and ‼︎ for user-facing
  warnings and errors, for example, but be sure to do it consistently.
  DO NOT use emojis gratuitously in comments or output.
  You may use then ONLY when they have clear meanings (like success or failure).
  Unless the user says otherwise, avoid emojis and Unicode in comments as clutters the
  output with little benefit.---
description: Python Coding Guidelines
---
# Python Coding Guidelines

These are rules for a modern Python project using uv.

## Python Version

Write for Python 3.11-3.13. Do NOT write code to support earlier versions of Python.
Always use modern Python practices appropriate for Python 3.11-3.13.

Always use full type annotations, generics, and other modern practices.

## Project Setup and Developer Workflows

- Important: BE SURE you read and understand the project setup by reading the
  pyproject.toml file and the Makefile.

- ALWAYS use uv for running all code and managing dependencies.
  Never use direct `pip` or `python` commands.

- Use modern uv commands: `uv sync`, `uv run ...`, etc.
  Prefer `uv add` over `uv pip install`.

- You may use the following shortcuts
  ```shell
  
  # Install all dependencies:
  make install
  
  # Run linting (with ruff) and type checking (with basedpyright).
  # Note when you run this, ruff will auto-format and sort imports, resolving any
  # linter warnings about import ordering:
  make lint
  
  # Run tests:
  make test

  # Validate docs
  make docs-check
  
  # Run uv sync, lint, and test, docs-check in one command:
  make
  ```

- The usual `make test` like standard pytest does not show test output.
  Run individual tests and see output with `uv run pytest -s some/file.py`.

- Always run `make lint` and `make test` to check your code after changes.

- You must verify there are zero linter warnings/errors or test failures before
  considering any task complete.

## General Development Practices

- Be sure to resolve the pyright (basedpyright) linter errors as you develop and make
  changes.

- If type checker errors are hard to resolve, you may add a comment `# pyright: ignore`
  to disable Pyright warnings or errors but ONLY if you know they are not a real problem
  and are difficult to fix.

- In special cases you may consider disabling it globally it in pyproject.toml but YOU
  MUST ASK FOR CONFIRMATION from the user before globally disabling lint or type checker
  rules.

- Never change an existing comment, pydoc, or a log statement, unless it is directly
  fixing the issue you are changing, or the user has asked you to clean up the code.
  Do not drop existing comments when editing code!
  And do not delete or change logging statements.

## Coding Conventions and Imports

- Always use full, absolute imports for paths.
  do NOT use `from .module1.module2 import ...`. Such relative paths make it hard to
  refactor. Use `from toplevel_pkg.module1.modlule2 import ...` instead.

- Be sure to import things like `Callable` and other types from the right modules,
  remembering that many are now in `collections.abc` or `typing_extensions`. For
  example: `from collections.abc import Callable, Coroutine`

- Use `typing_extensions` for things like `@override` (you need to use this, and not
  `typing` since we want to support Python 3.11).

- Add `from __future__ import annotations` on files with types whenever applicable.

- Use pathlib `Path` instead of strings.
  Use `Path(filename).read_text()` instead of two-line `with open(...)` blocks.

## Use Modern Python Practices

- ALWAYS use `@override` decorators to override methods from base classes.
  This is a modern Python practice and helps avoid bugs.


## Linting, Formatting, and Type Checking

This project uses a comprehensive set of tools to ensure code quality:

- codespell: Automatically checks and fixes spelling errors in code and documentation. Runs with --write-changes, so typos are auto-fixed.
- ruff check: Fast linter; runs with --fix to auto-fix where possible.
- ruff format: Formatter compatible with Black; formats code and sorts imports.
- basedpyright: Modern type checker; shows coverage stats with --stats.

All these run together via `make lint`. It will:
1. Fix spelling errors automatically
2. Fix lint issues where possible
3. Format all code consistently
4. Check types and report any errors

After `make lint`, address any remaining issues that couldn’t be auto-fixed. Prefer adding types over ignores; use `# pyright: ignore` only for justified false positives. See pyproject.toml for configured rules.

For test files prefer to fix the test-cases issues first before coming to fix the linting and type-checking issues.
As some type-checking issues are common for test-files, ignore specific rule for particular line in the test file. And if the same rule ignore needs to be ignores for more than 1 line then ignore it at file level.

File level pyright ignore can be written in this format, example `# pyright: reportUnusedVariable=false`.
Line specific pyright ignore can be written in this format, example `# pyright: ignore[reportMissingImports]`.


## Documentation & README

Use Sphinx with MyST Markdown (`.md`) to author documentation, and keep `README.md` aligned with user-facing behavior.

- Typical layout: a `docs/` directory with a `source/` (inputs) and `build/` (outputs) subdirectory.
- Theme: choose a modern Sphinx theme (for example, Furo) suitable for your audience.
- Parser/format: MyST Markdown via `myst_parser`.
- Helpful extensions often include: `sphinx.ext.autodoc`, `sphinx.ext.napoleon`, `sphinx.ext.intersphinx`, `sphinx.ext.viewcode`, `sphinx.ext.doctest`, `sphinx_copybutton`, `sphinx_autodoc_typehints`, and a Mermaid plugin.
- MyST features: enable the ones you need (e.g., `colon_fence` for colon directives, heading anchors for linkable headings).
- Static assets: keep CSS/images under a static directory (commonly `_static/`).
- Versioning: avoid hardcoding versions inside pages; prefer a single source of truth injected via Sphinx config.

### Authoring

- Write one top-level H1 per page. Use H2 and H3 for subsections.
- Add each page to a toctree (commonly in the project’s main index page). Example:
  ```md
  ```{toctree}
  :maxdepth: 2
  :caption: Guide

  overview
  usage
  troubleshooting
  ```
  ```
- Prefer Sphinx roles over raw URLs for cross-references:
  - Link to another page with `{doc}`: ``{doc}`overview``
  - Use intersphinx for external APIs (e.g., ``:py:class:`pathlib.Path``).
- Code blocks: use fenced blocks with language hints (`python`, `yaml`, `bash`, `json`) and keep examples copyable.
- Admonitions: use MyST directives, for example:
  ```md
  ```{note}
  Short helpful note.
  ```
  ```
  or colon-fence syntax:

  ::: tip
  Friendly tip.
  :::
- Mermaid diagrams: use the MyST directive and ensure the extension is enabled:
  ```md
  ```{mermaid}
  graph TD
    A[Start] --> B{Build}
    B -->|pass| C[Publish]
    B -->|fail| D[Fix]
  ```
  ```
- Images: store under a static folder and reference with a relative path (for example: ./_static/img.png).

### Build, validate, and preview

- Validate docs with Sphinx, ideally treating warnings as errors:
  ```bash
  make docs-check
  ```
- For live preview with auto-rebuild, use sphinx-autobuild:
  ```bash
  make docs-live
  ```

### Common pitfalls and fixes

- “Document isn’t included in any toctree” (orphan page): add the page to a toctree (often the main index page).
- Broken anchors to headings: if heading anchors aren’t available, add explicit labels or use `{ref}`.
- Unknown directive errors (admonitions/mermaid): verify the directive syntax and that the related extensions are enabled.
- Version drift in content: centralize versioning via Sphinx config or a single source, and reference it in pages.
- Image path issues: keep assets under a static directory and use correct relative paths from the page.

### When to update and how to validate

Whenever a change is user-facing, update docs and README in the same pull request.

- Update docs under `docs/source` when behavior, inputs/outputs, configuration, environment variables, supported versions, CLI/entry points, defaults, or migration/deprecation notes change. Keep examples and code snippets in sync, update toctrees/cross-references, and refresh screenshots/diagrams when UI/output changes.
- Update `README.md` for quickstart/installation, minimum supported versions, badges, primary usage examples, high-level configuration summary, and any copy-paste action usage snippets.
- Validate before submitting:
  - Run the docs validation task and ensure it passes with no warnings treated as errors: `make docs-check`.
  - Ensure `CHANGELOG.md` has an Unreleased entry matching the change and, when relevant, links to updated docs.
  - Confirm README and docs are consistent (no conflicting instructions).

## Changelog updates (Keep a Changelog)

- Always update `CHANGELOG.md` whenever a change is user-facing. This includes, but isn’t limited to:
  - Source code behavior changes (inputs/outputs, defaults, errors, messages, CLI/entry points, public APIs)
  - Configuration/schema or environment variable changes
  - Inputs changes
  - Behavioral changes
  - Logging format or content that users see
  - Documentation changes that affect how users use or understand the project (guides, examples, reference, navigation)
- Add entries under the Unreleased section using concise bullets. Prefer the standard categories:
  - Added, Changed, Fixed, Deprecated, Removed, Security
  - If a docs-only change is clearly user-facing, include it under Added/Changed (don’t hide it under internal changes).
- Keep entries short, specific, and actionable. Use imperative mood and avoid implementation detail.



## Testing

- For longer tests put them in a file like `tests/test_somename.py` in the `tests/`
  directory (or `tests/module_name/test_somename.py` file for a submodule).

- For simple tests, prefer inline functions in the original code file below a `## Tests`
  comment. This keeps the tests easy to maintain and close to the code.
  Inline tests should NOT import pytest or pytest fixtures as we do not want runtime
  dependency on pytest.

- DO NOT write one-off test code in extra files that are throwaway.

- DO NOT put `if __name__ == "__main__":` just for quick testing.
  Instead use the inline function tests and run them with `uv run pytest`.

- You can run such individual tests with `uv run pytest -s github_action_toolkit/.../path/to/test`

- Don’t add docs to assertions unless it’s not obvious what they’re checking - the
  assertion appears in the stack trace.
  Do NOT write `assert x == 5, "x should be 5"`. Do NOT write `assert x == 5 # Check if
  x is 5`. That is redundant.
  Just write `assert x == 5`.

- DO NOT write trivial or obvious tests that are evident directly from code, such as
  assertions that confirm the value of a constant setting.

- NEVER write `assert False`. If a test reaches an unexpected branch and must fail
  explicitly, `raise AssertionError("Some explanation")` instead.
  This is best typical best practice in Python since assertions can be removed with
  optimization.

- DO NOT use pytest fixtures like parameterized tests or expected exception decorators
  unless absolutely necessary in more complex tests.
  It is typically simpler to use simple assertions and put the checks inside the test.
  This is also preferable because then simple tests have no explicit pytest dependencies
  and can be placed in code anywhere.

- DO NOT write trivial tests that test something we know already works, like
  instantiating a Pydantic object.

  ```python
  class Link(BaseModel):
    url: str
    title: str = None
  
  # DO NOT write tests like this. They are trivial and only create clutter!
  def test_link_model():
    link = Link(url="https://example.com", title="Example")
    assert link.url == "https://example.com"
    assert link.title == "Example"
  ```

- Always add or update tests when introducing new functionality or changing user-facing behavior. Cover the happy path and at least one edge case for each new behavior.
- Do not modify tests for purely non-behavioral changes (formatting, refactors without behavior change, comments). If test updates seem necessary for such changes, reconsider the code change or justify the behavior change explicitly.
- Ensure the full test suite passes before considering a task complete. Use targeted runs for speed during development, but finish with the standard test task.


## Types and Type Annotations

- Use modern union syntax: `str | None` instead of `Optional[str]`, `dict[str]` instead
  of `Dict[str]`, `list[str]` instead of `List[str]`, etc.

- Never use/import `Optional` for new code.

- Use modern enums like `StrEnum` if appropriate.

- One exception to common practice on enums: If an enum has many values that are
  strings, and they have a literal value as a string (like in a JSON protocol), it’s
  fine to use lower_snake_case for enum values to match the actual value.
  This is more readable than LONG_ALL_CAPS_VALUES, and you can simply set the value to
  be the same as the name for each.
  For example:
  ```python
  class MediaType(Enum):
    """
    Media types. For broad categories only, to determine what processing
    is possible.
    """
  
    text = "text"
    image = "image"
    audio = "audio"
    video = "video"
    webpage = "webpage"
    binary = "binary"
  ```

## Guidelines for Literal Strings

- For multi-line strings NEVER put multi-line strings flush against the left margin.
  ALWAYS use a `dedent()` function to make it more readable.
  You may wish to add a `strip()` as well.
  Example:
  ```python
  from textwrap import dedent
  markdown_content = dedent("""
      # Title 1
      Some text.
      ## Subtitle 1.1
      More text.
      """).strip()
  ```


## Guidelines for Docstrings

- Here is an example of the correct style for docstrings:
  ```python
  def check_if_url(
      text: UnresolvedLocator, only_schemes: list[str] | None = None
  ) -> ParseResult | None:
      """
      Convenience function to check if a string or Path is a URL and if so return
      the `urlparse.ParseResult`.
  
      Also returns false for Paths, so that it's easy to use local paths and URLs
      (`Locator`s) interchangeably. Can provide `HTTP_ONLY` or `HTTP_OR_FILE` to
      restrict to only certain schemes.
      """
      # Function body
  
  def is_url(text: UnresolvedLocator, only_schemes: list[str] | None = None) -> bool:
      """
      Check if a string is a URL. For convenience, also returns false for
      Paths, so that it's easy to use local paths and URLs interchangeably.
      """
      return check_if_url(text, only_schemes) is not None
  ```

- Use concise pydoc strings with triple quotes on their own lines.

- Use `backticks` around variable names and inline code excerpts.

- Use plain fences (```) around code blocks inside of pydocs.

- For classes with many methods, use a concise docstring on the class that explains all
  the common information, and avoid repeating the same information on every method.

- Docstrings should provide context or as concisely as possible explain “why”, not
  obvious details evident from the class names, function names, parameter names, and
  type annotations.

- Docstrings *should* mention any key rationale or pitfalls when using the class or
  function.

- Avoid obvious or repetitive docstrings.
  Do NOT add pydocs that just repeat in English facts that are obvious from the function
  name, variable name, or types.
  That is silly and obvious and makes the code longer for no reason.

- Do NOT list args and return values if they’re obvious.
  In the above examples, you do not need and `Arguments:` or `Returns:` section, since
  sections as it is obvious from context.
  do list these if there are many arguments and their meaning isn’t clear.
  If it returns a less obvious type like a tuple, do explain in the pydoc.

- Exported/public variables, functions, or methods SHOULD have concise docstrings.
  Internal/local variables, functions, and methods DO NOT need docstrings unless their
  purpose is not obvious.

## General Clean Coding Practices

- Avoid writing trivial wrapper functions.
  For example, when writing a class DO NOT blindly make delegation methods around public
  member variables. DO NOT write methods like this:
  ```python
      def reassemble(self) -> str:
        """Call the original reassemble method."""
        return self.paragraph.reassemble()
  ```
  In general, the user can just call the enclosed objects methods, reducing code bloat.

- If a function does not use a parameter, but it should still be present, you can use `#
  pyright: ignore[reportUnusedParameter]` in a comment to suppress the linter warning.

## Guidelines for Backward Compatibility

- When changing code in a library or general function, if a change to an API or library
  will break backward compatibility, MENTION THIS to the user.

- DO NOT implement additional code for backward compatiblity (such as extra methods or
  variable aliases or comments about backward compatibility) UNLESS the user has
  confirmed that it is necessary.