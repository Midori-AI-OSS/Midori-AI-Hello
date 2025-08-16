# Implement multi-camera presence detection service

- Poll each configured camera for 1s using OpenCV and run the trained YOLO model to detect authorized users.
- Emit events when an authorized profile is seen or absent across all cameras.
- Adjust polling frequency: 10 s when a user is present, 5 s when absent for faster checks.
- Expose an async API that other components can subscribe to for presence updates.
- Reference: `.codex/planning/plan.md`, `.codex/planning/textual_review.md`.
