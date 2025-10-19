# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2025-10-18

### Added

- Additional forwarded methods: `__ne__`, `__hash__`, `__format__`, `__sizeof__`, `__copy__`, `__deepcopy__`
- Comprehensive tests for all newly forwarded methods

### Changed

- Improved `__bytes__` implementation documentation (implementation was already correct)

## [0.2.0] - 2025-10-18

### Changed

- **BREAKING**: Migrated from Poetry to uv with hatchling build backend
- Upgraded development status from Alpha to Beta
- Updated Python version support to 3.8-3.13 (added Python 3.13)
- Replaced black and flake8 with ruff for linting and formatting
- Updated pre-commit hooks to modern versions

### Added

- Comprehensive docstrings for all classes and methods
- `py.typed` marker for PEP 561 compliance (full type hint support)
- GitHub Actions CI/CD workflows for testing and publishing
- Test coverage reporting with pytest-cov
- This CHANGELOG.md file
- Project URLs for issues and changelog in package metadata

### Fixed

- Updated project classifiers to reflect current status
- Improved package metadata and documentation

## [0.1.2] - 2022-12-21

### Added

- Custom method forwarding with `extra_forwards` parameter
- Option to disable default method forwarding with `no_def_forwards`
- Comprehensive test coverage

### Fixed

- Various bug fixes and improvements

## [0.1.0] - 2022-12-15

### Added

- Initial release
- Runtime type checking for NewType pattern
- Transparent wrapper for existing types
- Method forwarding for magic methods
- Support for arithmetic, comparison, and container operations
- Zero dependencies

[Unreleased]: https://github.com/evanjpw/newertype/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/evanjpw/newertype/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/evanjpw/newertype/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/evanjpw/newertype/releases/tag/v0.1.2
[0.1.0]: https://github.com/evanjpw/newertype/releases/tag/v0.1.0
