# Secure authorized profile storage

- Serialize whitelist profiles under `~/.config/midori-ai/whitelist.json` and encrypt using a key derived from `sha256` of the trained model weights.
- Use `cryptography.fernet` for symmetric encryption; keep a temporary plaintext copy only during retraining, then re-encrypt with the new model hash.
- Expose TUI actions to add/remove users, trigger encryption/decryption, show when the stored hash differs from the active model, and regenerate the key after training completes.
- Reference: `.codex/planning/plan.md`.
