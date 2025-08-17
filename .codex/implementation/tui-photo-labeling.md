# TUI Photo Labeling

Provides a `CaptureScreen` used within `MidoriApp` for capturing images
from multiple cameras and writing YOLO-format labels.

- `list_cameras(max_devices=10)` probes sequential indices with
  `cv2.VideoCapture` to discover available cameras.
- `MidoriApp` falls back to `list_cameras()` when no cameras are
  configured in `config.yaml`, ensuring available webcams are detected.
- `save_sample` stores an image under
  `dataset/images/<camera_id>/` and writes a matching label file under
  `dataset/labels/<camera_id>/` with normalized face (`class 0`) and body
  (`class 1`) bounding boxes. Required directories are created automatically.
- `CaptureScreen` binds `c` to capture a frame and `n` to cycle cameras.
  On capture it loads the configured Ultralytics YOLO model to auto-detect
  face and body boxes. Detections are shown for confirmation and can be
  rejected to fall back to manual `cv2.selectROI` dialogs before prompting
  for the subject name.
  When no cameras are detected, the screen remains idle without
  attempting to open a device.
  Numeric camera IDs supplied as strings are coerced to integers, and
  `_open_camera` logs distinct warnings for missing OpenCV versus an
  empty camera list.

See planning notes in `.codex/planning/plan.md` and
`.codex/planning/textual_review.md` for the broader TUI design.
