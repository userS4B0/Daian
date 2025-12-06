# Changelog

All notable changes to this project will be documented in this file.

## [v0.1.0-alpha] - 2025-12-06

### What's Changed
- Basic Implement Todoist API Client by @userS4B0 in https://github.com/userS4B0/Daian/pull/1
- Integrate Google Calendar API client with event listing and normalization by @userS4B0 in https://github.com/userS4B0/Daian/pull/2
- Basic Log implementation by @userS4B0 in https://github.com/userS4B0/Daian/pull/3
- Add GitHub workflows and comprehensive unit tests by @userS4B0 in https://github.com/userS4B0/Daian/pull/4
- Core/task-duration by @userS4B0 in https://github.com/userS4B0/Daian/pull/10
- Core/cli-entrypoint by @userS4B0 in https://github.com/userS4B0/Daian/pull/11
- Initial project scaffolding and CLI (`daian_cli.py`)
- Todoist ingestion and basic task model
- Google Calendar OAuth2 integration and event creation
- Rule-based duration estimator and scheduling pipeline
- Docs: README, Roadmap, Project Diagram, .env examples
- CI: PEP8 Compliant workflows

### Known limitations
- Rule-based estimations (no ML yet)
- Limited error recovery and rollback
- No Docker/deployment automation
- No auto-assign tasks to calendar free schedule slots
- No unit tests support

**Full Changelog**: https://github.com/userS4B0/Daian/commits/v.0.1.0-alpha
