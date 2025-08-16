# Whitelist Management TUI

Integrates the `WhitelistManager` into the Textual application with a
screen for managing authorised profiles.

- Displays current whitelist entries and allows adding or removing names.
- Writes changes to encrypted storage using the model-derived key.
- Shows a status indicator when the stored whitelist hash differs from the
  active model and provides a button to re-encrypt.
