# KDE Wayland Screen Locker Review Guide

## Repository
- [KDE/kscreenlocker](https://github.com/KDE/kscreenlocker)

## Key Interfaces
### org.freedesktop.ScreenSaver
```xml
<method name="Lock"/>
<method name="GetSessionIdleTime"/>
<method name="Inhibit">
  <arg name="application_name" type="s" direction="in"/>
  <arg name="reason_for_inhibit" type="s" direction="in"/>
  <arg name="cookie" type="u" direction="out"/>
</method>
```

### Interface::Lock
```cpp
void Interface::Lock() {
    if (!KAuthorized::authorizeAction("lock_screen")) {
        return;
    }
    m_daemon->lock(calledFromDBus() ? EstablishLock::Immediate : EstablishLock::Delayed);
}
```

### Power Management Inhibition
`powermanagement_inhibition.cpp` and the `PowerInhibitor` helper in `interface.cpp` use the `org.kde.Solid.PowerManagement.PolicyAgent` service to keep the session awake while locked and release the inhibition cookie on exit.

## Review Steps for Task Masters
1. Clone the repo and inspect `dbus/org.freedesktop.ScreenSaver.xml` for DBus methods.
2. Review `interface.cpp` for lock/unlock and inhibition logic.
3. Examine `powermanagement_inhibition.cpp` for DBus calls that inhibit power management.
4. Confirm `ActiveChanged` signals for responding to lock/unlock events.
