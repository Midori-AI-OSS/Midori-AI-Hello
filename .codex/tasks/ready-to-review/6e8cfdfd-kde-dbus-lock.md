# Integrate KDE screen lock control

- Use DBus `org.freedesktop.ScreenSaver` methods `Lock`, `GetSessionIdleTime`, `Inhibit`, and `UnInhibit`; store the returned inhibition cookie.
- Subscribe to the `ActiveChanged` signal to respond to external locks/unlocks and mirror state in the TUI.
- Poll each configured camera every 10 s via the trained YOLO model; when no authorized face or body is detected on any feed, increase polling to every 5 s and issue a `Lock` after 30 s of absence.
- Unlock by calling `SetActive false` or `SimulateUserActivity` once an authorized user is recognized, and release the inhibition cookie via the `PowerInhibitor` helper when the app exits.
- Reference: `.codex/planning/plan.md`, `.codex/planning/kde_wayland_review.md`.
