# YOLO-assisted auto-labeling for photo capture

- Integrate the starter Ultralytics YOLO model into `CaptureScreen` so a captured frame is pre-scanned for face (`class 0`) and body (`class 1`) boxes before manual editing.
- After detection, prompt the user in the TUI for the person's name and allow correcting or confirming the bounding boxes.
- Persist the image under `photos/images/<camera_id>/` and write a matching YOLO-format label file under `photos/labels/<camera_id>/` using the chosen name.
- Automatically download the starter model if missing and create any `photos/` directories on demand so no manual file edits are required.
- When detection fails or hardware is unavailable, fall back to a manual labeling flow within the TUI rather than editing label files by hand.
- Reuse `save_sample` logic where possible and update `.codex/implementation/tui-photo-labeling.md` if behaviour changes.
- Reference: `.codex/planning/plan.md` and `.codex/implementation/tui-photo-labeling.md`.
