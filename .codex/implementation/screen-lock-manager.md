# Screen Lock State Manager

`ScreenLockManager` listens for presence detection events and controls the KDE
screen locker via `KDEScreenLocker`.

- Absence triggers a timer (~30 s) after which `Lock` is called.
- When an authorised user returns, the manager calls `SetActive false` to
  unlock the session.
- Lock state changes are reported back to the TUI through a callback so the
  current state can be displayed to the user.
