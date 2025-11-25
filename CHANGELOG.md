# Changelog

All notable changes to the Claude Plugins marketplace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.7] - 2025-11-25

### Important
- **RESTART REQUIRED**: Claude Code must be restarted after updating to this version for changes to take effect
- This version includes the same agent instruction fixes from 1.0.6, but clarifies that a restart is required to reload the updated instructions from disk into memory

### Notes
- If you updated from 1.0.5 to 1.0.6 and encountered agents not completing their work, restart Claude Code to resolve the issue
- The fixes are already in the code on disk, but Claude Code caches skill instructions in memory at startup

## [1.0.6] - 2025-11-25

### Fixed
- **meeting-transcriber**: Fixed transcript-cleaner agents not completing their work
  - Changed agent prompts from "use the transcript-cleaner skill" to direct step-by-step instructions
  - Agents now receive explicit instructions to use Read and Write tools
  - Added verification that agents actually execute tools rather than just describing what they would do
- **meeting-transcriber**: Improved chunk reassembly process
  - Made `cat` command the primary reassembly method (simpler and more reliable)
  - Added critical note about `--from-files` flag requirement for reassemble script
  - Fixed issue where reassemble script was called without proper flags

### Changed
- **meeting-transcriber**: Enhanced agent instructions with more explicit step-by-step guidance
- **meeting-transcriber**: Improved failure detection and retry instructions in checkpoint sections

## [1.0.5] - 2025-11-24

### Changed
- Major restructure for agent compliance
- Improved agent instructions and workflow

## [1.0.4] - 2025-11-23

### Fixed
- Fixed None values in filename and YAML frontmatter

## [1.0.3] - 2025-11-22

### Changed
- Improved chunk reassembly instructions to avoid token waste

## [1.0.2] - 2025-11-21

### Added
- Agent failure detection, retry logic, and validation

## [1.0.1] - 2025-11-20

### Added
- Initial release of meeting-transcriber plugin

## [1.0.0] - 2025-11-19

### Added
- Initial marketplace setup
