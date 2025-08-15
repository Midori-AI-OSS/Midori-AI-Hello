# KDE Screen Lock Control

`KDEScreenLocker` wraps the `org.freedesktop.ScreenSaver` interface using
`dbus-next`. The async helper connects to the session bus and exposes
`lock`, `get_idle_time`, `inhibit`, `uninhibit`, and
`add_active_changed_handler` methods. Callback functions passed to
`add_active_changed_handler` may be synchronous or async; coroutine
handlers are scheduled on the event loop. The `PowerInhibitor` context
manager provides automatic `inhibit`/`uninhibit` cleanup.

Tests mock a DBus connection so they run without a running KDE session.
