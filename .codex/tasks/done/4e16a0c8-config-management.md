# Implement config management and camera setup

- Define a `config.yaml` schema with `dataset`, `epochs`, `batch`, `idle_threshold`, `model`, `backend`, and `cameras` (list of up to 20 IDs).
- Add module to load and save config via a YAML library (e.g., `pyyaml`); expose helper to update individual settings.
- Build Textual screen for editing settings and managing camera list (add/remove/reorder).
- Persist camera-specific dataset directories under `dataset/images/<camera_id>` and `dataset/labels/<camera_id>`.
- Reference: `.codex/planning/plan.md`.
