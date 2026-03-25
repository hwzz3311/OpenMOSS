# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Team Knowledge Sharing** - New feature for team agents to share and search knowledge/experiences
  - Added `TeamKnowledge` data model with fields: id, team_id, title, content, author_agent_id, created_at, updated_at
  - Added service layer functions: create_knowledge, list_knowledge, get_knowledge, update_knowledge, delete_knowledge, search_knowledge, get_team_knowledge
  - Admin API endpoints: `/api/admin/teams/{team_id}/knowledge` (CRUD operations)
  - Agent API endpoints: `/api/teams/my/knowledge` (upload, list, search)
  - Cross-team search with team source identification (returns team_name for each result)
  - Search supports title keyword matching and content fuzzy matching
  - Frontend TeamsView now includes knowledge UI section
  - Proper team status checks (disabled team cannot access/ upload knowledge)

- **Agent Collaboration in Team Profile** - Team introduction template now includes role collaboration configuration
  - Added "角色协作配置" section with notification templates for each role (planner, executor, reviewer, patrol)
  - Added OpenClaw `agent` command examples for agent-to-agent notification
  - Complete notification flow: planner → executor → reviewer → patrol → planner
  - Planner can now receive notifications from executor (blockers), reviewer (rejection), patrol (task completion)

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
