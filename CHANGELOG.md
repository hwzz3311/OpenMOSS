# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-03-21

### Added

- **Agent Package Export** - New feature to generate OpenClaw agent workspace packages
  - Backend service (`app/services/agent_package_service.py`) for ZIP generation
  - New API endpoint: `GET /api/prompts/export/{slug}`
  - Frontend download button in "Prompt Preview" view
  - Package includes: IDENTITY.md, SOUL.md, AGENTS.md, USER.md, HEARTBEAT.md, BOOTSTRAP.md, TOOLS.md

- **Clipboard Fallback** - Added HTTP fallback for clipboard operations in non-HTTPS environments
  - Fixed "复制失败" (copy failed) issue in prompt management page
  - Uses `document.execCommand('copy')` as fallback when modern Clipboard API fails

- **Agent Onboarding Improvements** - Registration and onboarding enhancements
  - Fixed registration onboarding bugs
  - Added clipboard HTTP fallback for registration process

- **Executor Examples** - Added software developer executor prompt examples

### Changed

- **Frontend Build** - Updated static assets for UI improvements

### Fixed

- **Clipboard Issue** - Fixed copy functionality failing in "提示词管理" (Prompt Management) page
- **Registration Bugs** - Fixed various registration onboarding issues

---

## Previous Versions

[1.0.0]: https://github.com/uluckyXH/OpenMOSS/compare/v0.9.0...v1.0.0
