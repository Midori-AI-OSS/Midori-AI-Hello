# AUR Packaging

PKGBUILD builds the project from a pinned commit and installs a placeholder
TUI entry point using `uv` exclusively—system Python must not be invoked.

- Source: tarball for commit `38d3ee46cf79539e7d97f05aec9c1b2430b48ee9`.
- Build step uses `uv build --wheel`.
- Package step installs the wheel with
  `uv pip install --compile-bytecode --prefix="$pkgdir/usr"`,
  and adds a `/usr/bin/midori-ai-hello` script that launches the module
  via `uv run midori_ai_hello`.

The PKGBUILD was manually tested by building a wheel, installing it into a
temporary prefix with `uv pip install`, and running the installed
`/usr/bin/midori-ai-hello` launcher.

After modifying `PKGBUILD`, refresh hashes with `updpkgsums` and regenerate
`.SRCINFO` via `makepkg --printsrcinfo > aur/.SRCINFO`. Final verification
should happen in a clean Arch chroot with `makepkg -si`.
