# Add main menu to Textual interface

- Introduce a startup menu screen that explains how to add a face and provides options to:
  - capture photos,
  - manage the whitelist,
  - view training status,
  - quit the app.
- Replace or supplement global key bindings with menu navigation so new users have a clear entry point.
- Ensure existing screens (`CaptureScreen`, `WhitelistScreen`, etc.) are reachable from the menu and return back when done.
- Include a first-run setup or help path so users can configure cameras and whitelist entries without editing files.
- Provide clear fallbacks when no cameras or config are present, guiding users through fixes entirely within the menu.
- Update documentation in `.codex/implementation/tui-app-skeleton.md` to reflect the menu structure.
