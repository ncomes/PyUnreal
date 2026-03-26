# PyUnreal - Coding Guidelines

> Reference guide for Claude when writing Python code for this project.
> Mirrors MCAEditor conventions — see that project's CLAUDE.md for full details.

---

## Project Context

- **Pure Python package** — no C++ compilation, no Cython
- **Runs inside Unreal Engine's Python interpreter** — the `unreal` module only exists there
- **Open source, MIT license** — all code is public
- **Two-tier architecture**: works standalone for standard UE APIs; advanced features
  (AnimBP graph editing) require MCA Editor's C++ plugin (MCAEditorScripting)

---

## Core Rules

- **NO TYPE HINTS in function signatures.** Use Sphinx-style docstrings instead.
- **Heavy commenting** — every non-trivial block gets a comment explaining WHY.
- **Sphinx-style docstrings** on all modules, classes, and functions.
- **Section headers** for scanning long files: `# --- Name ---`
- **4 spaces** indentation, **120-char** soft line limit.
- **No emojis** in code or documentation.
- **Imports**: stdlib → third-party → local, one per line.
- **`unreal` is always a lazy import** — import inside functions/methods, never at module level.
  The package must be importable outside UE (for testing, docs generation).

---

## Docstring Format

```python
def create(package_path, asset_name, skeleton):
    """
    Create a new Animation Blueprint targeting the given skeleton.

    :param str package_path: Content Browser folder (e.g. '/Game/AnimBP')
    :param str asset_name: Name for the new AnimBP asset
    :param unreal.Skeleton skeleton: Skeleton asset to target
    :return: Wrapped AnimBlueprint instance
    :rtype: AnimBlueprint
    """
```

---

## Testing

- Tests run outside UE with a mocked `unreal` module.
- Use `unittest.mock` to patch `import unreal`.
- Tests must NOT require Unreal Engine to be running.
