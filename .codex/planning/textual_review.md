# Textual TUI Review Guide

## Repository
- [Textualize/textual](https://github.com/Textualize/textual)

## Highlights
- Cross-platform terminal and web UI from one codebase.
- Rich widget system with CSS-like styling and reactive events.
- Built-in testing tools for TUI components.
- Can interoperate with external libraries like OpenCV by running blocking tasks in worker threads.

## Review Steps for Task Masters
1. Clone the repo and read `README.md` for core concepts and examples.
2. Explore `examples/` to understand layout and widget usage.
3. Examine `src/textual/app.py` for the `App` base class and review widgets under `src/textual/widgets/`.
4. Check `examples/camera.py` or similar demos for handling image previews and async tasks.
5. Check `tests/` for patterns in testing interactive components.
