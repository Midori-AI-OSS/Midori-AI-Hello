# Textual App Skeleton

Introduces `MidoriApp`, a multi-screen Textual application that wraps the
capture interface and management screens:

- `CaptureScreen` handles image capture and YOLO label writing.
- `WhitelistScreen` manages authorised profiles with encrypted storage.
- Placeholder screen exists for training status.
- A `MainMenuScreen` appears on startup with menu navigation to capture,
  whitelist, training status, configuration, or exit. A global `m` binding
  returns to this menu from anywhere.
- Global bindings (`c`, `w`, `g`, `t`, `m`, `r`, `q`) switch screens, retrain,
  show the menu, or exit.
- `YOLOTrainingScheduler` runs in a background task with manual retrain via `r`.
