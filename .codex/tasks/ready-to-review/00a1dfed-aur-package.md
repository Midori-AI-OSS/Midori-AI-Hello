# Finalize AUR package

- Complete `aur/PKGBUILD` with `pkgname`, `pkgver()` function, `source` tarball URL,
  `sha256sums`, and `depends=('uv')`.
- Add `build()` and `package()` functions that build the wheel with `uv` and install
  via `uv pip install --compile-bytecode`, placing a `/usr/bin/midori-ai-hello`
  launcher that delegates to `uv run midori_ai_hello`.
- Run `updpkgsums` then generate `.SRCINFO` via `makepkg --printsrcinfo > .SRCINFO`.
- Use `makepkg -si` inside a clean Arch chroot to verify installation and runtime,
  confirming that DBus calls and training can be invoked.
- Reference: `.codex/planning/aur_packaging_review.md`.
