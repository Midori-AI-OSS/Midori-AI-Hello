# Presence Detection Service

Detects authorised users across all configured cameras and emits presence events.

- Polls each camera for a single frame and runs the configured YOLO model.
- If any detection matches a whitelist entry, "present" is emitted; otherwise "absent".
- Polling interval is 10 s while present and 5 s when absent to re-check sooner.
- Listeners register via `add_listener` and are called with a boolean state.
