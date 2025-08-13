# Build YOLO training scheduler

- Use the Ultralytics `YOLO` Python API and its `engine/trainer.py` (`DetectionTrainer`) to train on CPU (`device='cpu'`) against the dataset of labeled faces and full bodies aggregated from all camera folders. Allow switching to the YOLOv9 CLI (`train.py --device cpu`) for experimentation.
- Implement an idle monitor that checks `GetSessionIdleTime` via DBus and triggers training when idle exceeds the configured threshold or when the user requests retraining in the TUI.
- Load settings such as dataset path, epochs, batch size, and idle threshold from `config.toml` using `tomllib`; generate a temporary YAML file pointing to all `dataset/images/**` and `dataset/labels/**` before each training run.
- After training, save new weights, update the whitelist profile hash, and mark dataset entries with the last trained epoch.
- Reference: `.codex/planning/plan.md`, `.codex/planning/yolo_models_review.md`.
