

This is a new application and you must not consider migrations or backwards compatibility.
Design all new features with maintainability and performance in mind.
Use KISS, DRY, SOLID and YAGNI principles.
When refactoring, you can break backwards compatibility.
Always consider a better design approach compared to the existing one.
Consider multiple approaches, review them against the principles above, the existing methods and the overall architecture - and choose the best one.
When in doubt, ask for a review of your design approach before implementing it.

# Redis
You can not use LUA scripts!

# collections.abc
If sensible, implement collections.abc interfaces for your classes, such as MutableMapping or MutableSequence.

# Testing

To run tests use
- `uv run pytest tests/`

Tests can run for up to 5 minutes - be patient!

When designing new tests, read the old tests first to understand the existing patterns.
Use `pytest.mark.parametrize` to avoid code duplication.
Tests should be very specific and test only one thing.
Avoid complex test setups.
Each test must be a function, not a method of a class!

# Documentation
Use numpy style docstrings.
Docstrings must be concise and to the point.
Use type hints wherever possible. `import typing as t` if necessary, but use `list[int|float] | None` instead of `t.Optional[t.List[int|float]]`!

Do not create a summary file for the implemented features, unless specifically requested!
