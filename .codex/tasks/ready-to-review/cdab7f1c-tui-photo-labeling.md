# Implement photo capture and labeling TUI

- Build a Textual `App` that presents controls to preview **and switch between** multiple cameras via `opencv-python` (`cv2.VideoCapture`).
- When an image is captured, open `cv2.selectROI` dialogs so the user can draw bounding boxes around both the face and the full body.
- After the boxes are confirmed, prompt for the subject’s name from the whitelist and write image files to `dataset/images/<camera_id>/` with matching YOLO-format label file(s) (`class x_center y_center width height`, normalized 0–1) in `dataset/labels/<camera_id>/`.
- List existing images grouped by user and camera and allow deletion, relabeling, or re-boxing; maintain a JSON index tracking whether each sample has been used in training and the last epoch it was trained on.
- Reference: `.codex/planning/plan.md`, `.codex/planning/textual_review.md`.
