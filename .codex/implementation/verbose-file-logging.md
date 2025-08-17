# Verbose File Logging

Adds configurable logging that writes all debug output to `midori-ai-hello.log` while controlling console verbosity with `--log-level` or the `LOG_LEVEL` environment variable.

- Log file is created in the current working directory.
- Console defaults to `INFO`; pass `--log-level DEBUG` for more detail.
- Modules emit additional debug information for camera setup and capture actions.
- Additional components such as the Textual app, screen lock manager, training
  scheduler, DBus helper, and whitelist manager now log key lifecycle events.
