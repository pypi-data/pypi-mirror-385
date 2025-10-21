# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions CI/CD workflow for automatic PyPI publishing
- Dynamic version configuration using hatchling

### Changed
- Updated pyproject.toml to support dynamic version reading

### Deprecated

### Removed

### Fixed

### Security

## [0.2.0] - 2024-10-21

### Added
- Protocol-oriented + Mixin architecture refactoring
- Structured JSON output support with Pydantic schemas
- GLM model support via prompt engineering
- Enhanced image format detection
- Unicode-safe text processing for Windows console
- Privacy-focused git configuration (tests excluded)

### Changed
- Complete architectural overhaul from pipeline-based to protocol-oriented design
- Moved from embedded processing to external flow control
- Enhanced configuration system with structured output options

### Fixed
- Binary data display issues in console output
- OpenAI API message format for multimodal content
- JSON parsing with newline characters in GLM responses
- Unicode encoding issues in test output

### Deprecated
- Legacy OpenAIPipeline (marked for future removal)

## [0.1.0a3] - Previous

### Added
- Initial release with basic pipeline functionality
- OpenAI-compatible AI processing
- Dynamic batch processing
- docpipe-mini integration