# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2025-10-19

### Added
- Comprehensive troubleshooting documentation for macOS users
- macOS-specific installation guide with uv and pip instructions
- Quick fix guide for tiktoken dependency issues
- requirements.txt file for alternative installation
- MANIFEST.in for proper package distribution

### Changed
- Switched build backend from `setuptools` to `hatchling` for better compatibility with uv and modern Python packaging
- Enhanced package distribution configuration to ensure cross-platform compatibility
- Updated README with troubleshooting section and quick fixes

### Fixed
- Fixed tiktoken dependency issues on macOS by improving build configuration
- Improved package distribution to ensure platform-specific dependencies (like tiktoken) are correctly installed
- Added proper build system configuration for packages with compiled extensions

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.1.0] - 2025-10-19

### Added
- Initial release of docbt
- Multi-LLM support (OpenAI, Ollama, LM Studio)
- Interactive chat interface with Streamlit
- Data upload and analysis capabilities
- DBT documentation generation
- Developer mode with advanced settings
- Token usage monitoring
- Chain of Thought reasoning display
- Docker support with multi-stage builds
- Snowflake and BigQuery connectors (optional)
- CI/CD pipeline with GitHub Actions
- Automated testing with pytest on pull requests
- Code quality checks with Ruff
- Docker image builds on pull requests
- Manual release workflow for PyPI and Docker registries
