# YOLO Training Scheduler

- Loads `config.toml` for dataset path, epochs, batch size, model weights, idle threshold, and profile hash output.
- Generates a temporary dataset YAML pointing `train` and `val` to `dataset/images` and `dataset/labels`.
- Polls `GetSessionIdleTime` via `KDEScreenLocker`; when idle exceeds the threshold or training is forced, runs CPU-only training.
- Uses Ultralytics `YOLO` by default but can fall back to the YOLOv9 CLI when `backend = "yolov9"`.
- After training, saves the SHA-256 hash of `last.pt` to `profile.hash` and notes the last trained epoch in `dataset/metadata.json`.
