# Build screen lock state manager

- Subscribe to presence detection service events and decide when to call KDE `Lock` or `SetActive false`.
- Lock after ~30 s of absence and unlock shortly after an authorized user is detected.
- Mirror current lock state within the TUI and display status messages.
- Reference: `.codex/planning/plan.md`, `.codex/planning/kde_wayland_review.md`.
