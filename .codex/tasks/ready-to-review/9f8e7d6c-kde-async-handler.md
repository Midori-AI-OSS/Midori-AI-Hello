# Fix async handler scheduling in KDE lock client

- ensure `add_active_changed_handler` schedules coroutine callbacks with `asyncio.create_task`
- document async callback support

## Testing
- `uv run pytest`
