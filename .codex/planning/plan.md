# Midori AI Vision TUI Plan

## Goal
Create a Rich-based TUI application that captures images from the user, maintains a dataset, and trains a YOLO model when the system is idle. The app should manage screen locking on KDE Wayland and prevent the system from sleeping while active.

## Components
- **TUI Layer:** Use the [Textual](https://github.com/Textualize/textual) framework for a rich terminal interface.
- **Model:** Start with Ultralytics YOLO (v8 or newer). Allow replacement with other YOLO variants.
- **Dataset Management:** Allow users to add existing images or capture new photos through the TUI. After each capture, display the photo and let the user draw bounding boxes around the person’s face **and full body** using an OpenCV `selectROI` window or keyboard controls. Tag each box with the selected user name and write YOLO-format label file(s) (`class x_center y_center width height`, normalized 0–1) under `dataset/labels/` while saving the image under `dataset/images/`. Track whether each sample has been used in training and log the last epoch trained.
- **Camera Management:** Support multiple cameras (aim for up to 20 views). Provide TUI controls to select a camera for capture and store images and labels under camera-specific subdirectories. Presence detection should scan all configured cameras.
- **Access Control:** Maintain a whitelist of authorized users who can unlock the session. Provide TUI actions to add or remove allowed individuals.
- **Profile Storage:** Encrypt authorized user profiles with a hash derived from the trained model. During retraining, keep a temporary unencrypted backup and re-encrypt once complete.
- **Training Scheduler:**
  - Train on CPU during idle periods or when the user requests retraining.
  - Config file (e.g., `config.toml`) stores paths, idle threshold, epoch counts, and hardware settings.
- **Screen Lock Control:**
  - Detect authorized user presence with the model across all configured cameras.
  - Poll each camera for 1s every 10s. If no authorized user is seen on any feed, increase checks to every 5s for 1s until return.
  - Unlock after a short delay when a permitted user sits down.
  - Lock after ~30s of absence.
- **Sleep Inhibition:** Use `org.freedesktop.ScreenSaver.Inhibit` to keep the system awake while the app runs.
- **Packaging:** Ship an Arch Linux AUR package in an `aur/` folder targeting KDE Wayland on Arch.

## Open Questions
- Balancing training time with usability on low-end CPUs.
