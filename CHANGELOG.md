# Changelog

All notable changes to the Claude Plugins marketplace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.14] - 2025-11-26

### Important
- **RESTART REQUIRED**: Claude Code must be restarted after updating to this version for changes to take effect

### Fixed
- **meeting-transcriber**: Completely restructured post-agent workflow to prevent orchestrating agent from skipping critical steps
  - Root cause: Orchestrating agent skipped CHECKPOINT 1 verification and Step 2A-2 reassembly instructions entirely
  - Agent pattern-matched on "need to reassemble" after agents completed, ignoring all explicit instructions
  - Solution: Consolidated verification and reassembly into immediate post-agent ACTION steps with triple emoji warnings
  - New structure: "AFTER AGENTS COMPLETE: FOLLOW THESE STEPS IMMEDIATELY" with ACTION 1, 2, 3, 4
  - Added explicit failure conditions: "YOU HAVE FAILED if you used Read tool on chunk files"
  - Automatic fallback: Copy original chunks for any missing cleaned files (prevents content loss)
  - Result: Forces sequential execution - verify count, create fallbacks, run cat, verify word count

- **meeting-transcriber**: Strengthened transcript-cleaner agent spawning to prevent inconsistent prompt usage
  - Root cause: Half the agents (9 of 18) used short "Use the skill" prompts despite ultra-explicit instructions
  - Added triple emoji warning header before Task tool creation
  - Expanded failure pattern examples to show exactly what NOT to do
  - Added explicit check-before-submit section: "Check your Task tool calls before submitting"
  - Added post-prompt reminder: "USE THE FULL PROMPT ABOVE FOR EVERY CHUNK"
  - Result: Every chunk should now get full multi-line prompt with STEP 1-4

### Technical Details
V1.0.13 completely failed because the orchestrating agent never reached the restructured Step 2A-2 instructions. After launching cleaning agents, it immediately pattern-matched on "reassemble chunks" and read all 18 chunk files, skipping both CHECKPOINT 1 (verification) and Step 2A-2 (cat command). The agent treats meeting-transcriber.md as reference context rather than sequential instructions.

V1.0.14 addresses this by embedding verification and reassembly as immediate post-agent ACTIONS with overwhelming visual prominence (triple emoji warnings, failure conditions at end). The agent can no longer complete "launch agents" without immediately seeing "YOUR NEXT ACTIONS" with verification and cat commands.

Additionally, 50% of transcript-cleaner agents were failing with "0 tool uses" because the orchestrating agent inconsistently applied prompts even within the same batch. V1.0.14 adds multiple checkpoints reminding the agent to use full prompts for ALL chunks.

## [1.0.13] - 2025-11-26

### Important
- **RESTART REQUIRED**: Claude Code must be restarted after updating to this version for changes to take effect

### Fixed
- **meeting-transcriber**: Restructured Step 2A-2 reassembly instructions to prevent token waste
  - Root cause: Agent read all 18 chunk files (20k+ tokens) instead of using cat command
  - Solution: Lead with explicit bash command, numbered steps, prohibition at top
  - Pattern: Apply same ultra-explicit structure that worked for transcript-cleaner
  - Result: Reassembly now uses 0 additional tokens instead of 20k tokens
  - Prevents context overflow on large transcripts

### Technical Details
Despite clear warnings not to use Read tool, the orchestrating agent pattern-matched on "reassemble chunks" and read all files into context. The v1.0.13 restructure mirrors the successful transcript-cleaner pattern: prohibition first, command first, explanation second, with explicit failure conditions.

## [1.0.12] - 2025-11-26

### Important
- **RESTART REQUIRED**: Claude Code must be restarted after updating to this version for changes to take effect

### Fixed
- **meeting-transcriber**: Removed skill names from section headers to eliminate pattern matching
  - Changed "Step 2D: Launch People Normalizer" → "Step 2D: Normalize Participant Names"
  - Changed "Step 2E: Launch Meeting Notes Generator" → "Step 2E: Generate Meeting Notes"
  - Root cause: Section headers containing skill names triggered agents to create "Use the X skill" prompts, overriding the direct instructions below
  - This applies the same successful pattern from v1.0.10 (which fixed transcript-cleaner) to Steps 2D and 2E
  - All three agent types now use generic, action-based headers without skill name triggers

### Technical Details
While v1.0.11 added prohibition warnings and direct instructions, it retained skill names in the section headers for Steps 2D and 2E. The orchestrating agent pattern-matched on these header names first, ignoring the instructions below. v1.0.10 proved that removing "transcript-cleaner" from the header eliminated this behavior. v1.0.12 completes this fix by applying the same approach to people-normalizer and meeting-notes-generator headers.

## [1.0.11] - 2025-11-26

### Important
- **RESTART REQUIRED**: Claude Code must be restarted after updating to this version for changes to take effect

### Fixed
- **meeting-transcriber**: Applied same fix to people-normalizer (Step 2D) and meeting-notes-generator (Step 2E)
  - Removed "Use the X skill" pattern from agent spawning prompts
  - Replaced with direct, step-by-step instructions
  - Added prohibition headers: "DO NOT create prompts like 'Use the X skill'"
  - Ensures consistency across all agent launches (transcript-cleaner, people-normalizer, meeting-notes-generator)
  - While people-normalizer was working in v1.0.10, this change eliminates the confusing "use skill" pattern entirely

### Technical Details
v1.0.10 fixed transcript-cleaner but Steps 2D and 2E still used "Use the X skill" prompts. v1.0.11 completes the refactor by providing direct instructions for all agent types, eliminating any ambiguity about whether agents should invoke skills vs use tools directly.

## [1.0.10] - 2025-11-25

### Important
- **RESTART REQUIRED**: Claude Code must be restarted after updating to this version for changes to take effect

### Fixed
- **meeting-transcriber**: Ultra-explicit agent spawning instructions to prevent misinterpretation
  - Root cause: Section header "transcript-cleaner" triggered agents to create short prompts like "Use the transcript-cleaner skill..." instead of copying full instructions
  - Changed header to generic "Launch Cleaning Agents for Each Chunk" to avoid triggering skill invocation pattern
  - Added prominent prohibition section: "CRITICAL: DO NOT CREATE SHORT PROMPTS" with explicit examples of what NOT to do
  - Moved complete example Task tool call to TOP (before copyable text) so agents see expected result first
  - Added ultra-explicit copying instruction: "COPY THE TEXT BELOW EXACTLY, WORD FOR WORD, CHARACTER FOR CHARACTER"
  - Added explicit failure condition: "If your Task tool prompt contains phrases like 'use the skill', YOU HAVE FAILED"
  - This should finally resolve the issue where 3/18 chunks (4, 7, 10 in v1.0.9 test) failed with 0 tool uses

### Technical Details
The v1.0.9 START/END PROMPT markers were not sufficient because the section header itself ("Agents B1-BN: transcript-cleaner") was triggering the wrong interpretation. The word "transcript-cleaner" in the header caused orchestrating agents to think they should invoke that skill, overriding all instructions below. v1.0.10 eliminates the trigger word from the header and adds multiple layers of explicit prohibition to make misinterpretation impossible.

## [1.0.9] - 2025-11-25

### Important
- **RESTART REQUIRED**: Claude Code must be restarted after updating to this version for changes to take effect

### Fixed
- **meeting-transcriber**: Significantly strengthened transcript-cleaner agent prompts
  - Added START/END PROMPT markers to eliminate ambiguity about what text to copy
  - Included complete example Task tool call showing exact format
  - Made TASK TOOL PARAMETERS section explicit and prominent
  - Should resolve remaining cases of agents not executing tools (chunks 7, 8, 10, 11, 13, 14, 17, 18 in previous run)

- **transcript-cleaner**: Added strong word count guardrails
  - New prominent warning section if reduction exceeds 10%
  - Explicit instructions to add content back if over-reduced
  - Clear examples of what NOT to do (removing contextual phrases)
  - Guidance for transcripts with few filler words (0-5% reduction is better than 10%)
  - Should prevent chunks from summarizing instead of cleaning (previous chunks 11, 14, 16 had 14-22% reduction)

- **people-normalizer**: Made tool usage requirements explicit and mandatory
  - Added "STOP - READ THIS FIRST" section at top of skill
  - Explicitly states: "YOU WILL FAIL if you don't use Glob tool"
  - Added example Glob tool call with exact syntax
  - Clarified that agents cannot guess which names exist - must check vault
  - Should prevent agents from just formatting names without checking People directory

- **meeting-transcriber**: Enhanced reassembly instructions to prevent context waste
  - Added triple warning emoji header: "DO NOT READ CHUNK FILES INTO CONTEXT"
  - Made cat command the PRIMARY METHOD (emphasized as RECOMMENDED)
  - Added explicit warning about token waste (20,000 tokens for 18 files)
  - Included concrete examples with actual paths
  - Demoted reassemble script to ALTERNATIVE METHOD section
  - Should prevent agents from reading all chunk files before reassembly

### Changed
- **meeting-transcriber**: Restructured transcript-cleaner spawning instructions
  - Clearer section hierarchy (TASK TOOL PARAMETERS, prompt markers, placeholder guide, example)
  - More explicit placeholder replacement instructions
  - Concrete example showing full Task tool call for chunk 1

### Technical Details
All four issues identified in v1.0.8 analysis have been addressed:
1. Inconsistent tool execution → Strengthened prompt format with examples
2. Word count preservation failures → Added guardrails and recovery instructions
3. People normalizer not using vault → Made Glob tool usage mandatory with examples
4. Inefficient context usage → Emphasized cat command, warned against Read tool

## [1.0.8] - 2025-11-25

### Important
- **RESTART REQUIRED**: Claude Code must be restarted after updating to this version for changes to take effect

### Fixed
- **meeting-transcriber**: Fixed transcript-cleaner agent prompts not using direct instructions
  - Root cause: Agent instructions said "(SEE DIRECT INSTRUCTIONS BELOW)" which caused agents to create their own interpretation instead of copying the full prompt
  - Solution: Embedded the full step-by-step instructions directly inline in the prompt field
  - Agents now receive the complete cleaning instructions without ambiguity
  - This should resolve the issue where some chunks succeeded (using direct tools) while others failed (trying to invoke skills)

### Changed
- **meeting-transcriber**: Improved clarity of agent spawning instructions
  - Made it explicit that agents should copy the full prompt text with placeholders replaced
  - Added clear placeholder replacement instructions

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
