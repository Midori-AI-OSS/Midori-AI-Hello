# TUI Photo Labeling

Provides a `CaptureScreen` used within `MidoriApp` for capturing images
from multiple cameras and writing YOLO-format labels.

- `list_cameras(max_devices=10)` probes sequential indices with
  `cv2.VideoCapture` to discover available cameras.
- `save_sample` stores an image under
  `dataset/images/<camera_id>/` and writes a matching label file under
  `dataset/labels/<camera_id>/` with normalized face (`class 0`) and body
  (`class 1`) bounding boxes.
- `CaptureScreen` binds `c` to capture a frame and `n` to cycle cameras.
  Capturing opens `cv2.selectROI` dialogs for face and body regions
  before prompting for the subject name.

See planning notes in `.codex/planning/plan.md` and
`.codex/planning/textual_review.md` for the broader TUI design.
