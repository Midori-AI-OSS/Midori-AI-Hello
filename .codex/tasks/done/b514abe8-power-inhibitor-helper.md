# Add PowerInhibitor helper for KDE

- Call `org.freedesktop.ScreenSaver.Inhibit` to keep the system awake while the app runs.
- Store the returned inhibition cookie and release it with `UnInhibit` when exiting.
- Wrap logic in a context manager or helper class used by the Textual app.
- Reference: `.codex/planning/kde_wayland_review.md`.
