# Task Master Notes - 2025-08-16

Reviewed repository planning documents and existing tasks. Added three new tasks to expand the Midori AI Hello application:

1. Config management and camera setup
2. Whitelist management TUI
3. Textual app skeleton and navigation

Each task placed in `.codex/tasks/` with random hash prefixes.

2025-08-16: Updated config management task to use a YAML-based configuration per feedback rejecting TOML.

2025-08-16: Added tasks for presence detection service, power inhibition helper, and screen lock state manager.
2025-08-16: Completed power inhibition helper; CLI now runs inside `PowerInhibitor` and task moved to done.
2025-08-16: Completed screen lock state manager; app mirrors lock state and reacts to presence events.
2025-08-16: Completed presence detection service; multi-camera YOLO scans emit authorised-user events.
