# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-26

### Added
- Initial release of the SDK
- Core functionality for test set access
- Basic documentation and examples
- Basic unit tests and integration tests

## [0.1.1] - 2025-02-17

### Added
- Added support for Parquet files
- Added more entities and functionality

## [0.1.2] - 2025-02-18

### Added
- Added new topic entity
- Added base entity for CRUD testing
- Added topic tests

## [0.1.3] - 2025-02-19

### Added
- Added new test set capabilities
- Added PromptSynthesizer for generating test sets from prompts
- Added example usage for PromptSynthesizer

## [0.1.4] - 2025-02-20

### Added
- Added CLI scaffolding for rhesis

## [0.1.5] - 2025-02-21

### Added
- Added ParaphrasingSynthesizer for generating paraphrases of test cases

## [0.1.6] - 2025-04-14

### Added
- Added run method to LLM Service for improved convenience
- Added new Prompt and Test entity classes
- Added automatic test set description generation
- Added set_attributes() method to TestSet class
- Added support for custom system prompts in synthesizers

### Changed
- Changed TestSet to work with tests instead of prompts
- Changed synthesizers to use new test-focused entity model
- Changed prompt templates to match new test entity format

### Removed
- Removed direct prompt handling from TestSet class
- Removed old prompt-based test set generation

### Fixed
- Fixed synthesizer response parsing to handle new test structure
- Fixed test set property extraction to work with nested test objects

[0.1.0]: https://github.com/rhesis-ai/rhesis-sdk/releases/tag/v0.1.0
[0.1.1]: https://github.com/rhesis-ai/rhesis-sdk/releases/tag/v0.1.1
[0.1.2]: https://github.com/rhesis-ai/rhesis-sdk/releases/tag/v0.1.2
[0.1.3]: https://github.com/rhesis-ai/rhesis-sdk/releases/tag/v0.1.3
[0.1.4]: https://github.com/rhesis-ai/rhesis-sdk/releases/tag/v0.1.4
[0.1.5]: https://github.com/rhesis-ai/rhesis-sdk/releases/tag/v0.1.5
[0.1.6]: https://github.com/rhesis-ai/rhesis-sdk/releases/tag/v0.1.6
