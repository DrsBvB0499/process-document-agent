# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- JSON-to-Mermaid diagram converter for flowchart rendering
- Support for both Anthropic (Claude) and OpenAI APIs
- Automatic outputs directory creation
- Comprehensive error handling for API calls
- Model provider selection via CLI

### Fixed
- Flowchart image embedding in Word documents
- Windows encoding issues with emoji output
- Reserved keyword conflicts in Mermaid diagram styles

## [0.1.0] - 2026-02-06

### Added
- Initial release of Process Analysis Agent
- Conversational CLI for process documentation
- SIPOC analysis extraction
- AS-IS process map generation
- Baseline metrics collection
- Word document generation with embedded diagrams
- Process flowchart visualization with Pillow
- Session save/load functionality

### Features
- Phase 1: Conversational agent with SIPOC, Process Map, Baseline
- Phase 1b: Document generation (Word + visual flowchart)
