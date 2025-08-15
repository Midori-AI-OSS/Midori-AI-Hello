# Profile Encryption

Implements encrypted storage for the whitelist of authorised users.

- Profiles are stored in `~/.midoriai/whitelist.json`.
- The encryption key derives from the SHA512 hash of the model weights
  combined with the SHA512 hash of a persistent secret in
  `~/.midoriai/hellouuid.txt` (two newline-separated UUID4 values). If the
  secret file is missing it is created once and reused thereafter.
- `cryptography.fernet` handles symmetric encryption.
- A companion `whitelist.hash` file records the hash used so the
  application can detect when the active model changes.
- `WhitelistManager` exposes helpers to add/remove users, list users,
  check for hash mismatches, and re-encrypt when the model updates.
