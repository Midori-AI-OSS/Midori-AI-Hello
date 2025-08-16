# Textual App Skeleton

Introduces `MidoriApp`, a multi-screen Textual application that wraps the
capture interface and management screens:

- `CaptureScreen` handles image capture and YOLO label writing.
- `WhitelistScreen` manages authorised profiles with encrypted storage.
- Placeholder screen exists for training status.
- Global bindings (`c`, `w`, `g`, `t`, `r`, `q`) switch screens, retrain, or exit.
- `YOLOTrainingScheduler` runs in a background task with manual retrain via `r`.
