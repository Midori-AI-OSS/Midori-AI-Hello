# AUR Packaging Review Guide

## Resources
- [Arch PKGBUILD guidelines](https://wiki.archlinux.org/title/PKGBUILD)
- [AUR submission guide](https://wiki.archlinux.org/title/Arch_User_Repository)

## Review Steps for Task Masters
1. Survey existing AUR packages for Python-based TUIs to mirror directory structure and dependencies.
2. Draft a `PKGBUILD` with `pkgname`, `pkgver`, `source`, `sha256sums`, `depends=('uv')`, and an install step for the CLI entry point.
3. Generate `.SRCINFO` via `makepkg --printsrcinfo > .SRCINFO` and ensure both files stay in sync.
4. Test the package in a clean Arch chroot before publishing to the AUR.
