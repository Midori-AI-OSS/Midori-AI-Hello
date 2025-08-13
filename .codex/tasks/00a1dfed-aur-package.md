# Finalize AUR package

- Complete `aur/PKGBUILD` with `pkgname`, `pkgver()` function, `source` tarball URL, `sha256sums`, and `depends=('uv')`.
- Add `build()` and `package()` functions that install the Textual TUI entry point under `/usr/bin`.
- Run `updpkgsums` then generate `.SRCINFO` via `makepkg --printsrcinfo > .SRCINFO`.
- Use `makepkg -si` inside a clean Arch chroot to verify installation and runtime, confirming that DBus calls and training can be invoked.
- Reference: `.codex/planning/aur_packaging_review.md`.
