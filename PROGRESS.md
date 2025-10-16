# MPLACE Progress Tracking

This document tracks the progress of key tasks in the MPLACE project.

## Current Status

| Priority | Item                             | Status         | Details                                                                                      |
|----------|----------------------------------|----------------|----------------------------------------------------------------------------------------------|
| High     | Implement MVC Architecture       | Not done yet   | UI, logic, and I/O are still coupled across main.py, WindowGenDZN.py, and WindowVisuals.py; no clear Model/View/Controller separation observed. |
| High     | Add Comprehensive Error Handling | Done (partial) | Many file and subprocess operations wrapped with try/except and user-facing error dialogs (tk.messagebox) plus exception chaining in utility.py; some broad except remain in visualization code paths that could be narrowed (e.g., generic except in WindowVisuals.draw_plates alpha mapping and cleanup). |
| High     | Improve Resource Management      | Partially done | Matplotlib figures saved via fig.savefig and GUI canvases cleaned up with explicit cleanup (cleanup_canvas_widgets) and pyplot.close('all'); context managers used for file writes; however, a few generic try/except without finally in cleanup and some implicit resource lifetimes remain. |
| Medium   | Code Style Standardization      | Done (partial) | Consistent function docstrings in utility.py; clearer names and comments; still mixed styles in some files and a few legacy patterns. |
| Medium   | Add Comprehensive Type Hints    | Not done       | Type hints are not present in function signatures (e.g., transform_coordinate, read_csv_file, run_cmd) across modules. |
| Medium   | Implement Consistent Naming Conventions | Partially done | Generally consistent snake_case for functions; some UI variables and labels follow mixed naming; constants mostly lowercase lists (letters_capital) could be UPPER_CASE. |
| Medium   | Configuration Management         | Partially done | paths.ini parsing centralized in utility.read_paths_ini_file with clearer error messages; still no dedicated config module or validation schema; GUI holds configuration state. |
| Low      | Performance Optimizations       | Not done       | No apparent performance-specific work; visualization likely fine for typical plate sizes; no caching or vectorization beyond basic numpy usage. |
| Low      | Enhanced User Experience         | Not done       | Core flows functional; user messages improved on errors; no UX enhancements like progress indicators beyond simple labels; fixed save paths for PNG still a limitation. |

## Analysis Notes

### Error Handling Assessment
- **Strengths**: utility.py uses specific exceptions and clear messages for CSV/DZN reading and MiniZinc invocation; run_cmd wraps subprocess errors and returns decoded output; read_paths_ini_file handles missing file with helpful error. main.py and WindowGenDZN.py catch specific exceptions and display tk.messagebox dialogs; writes use context managers.
- **Areas for improvement**: Some places use generic `except` in WindowVisuals (fallbacks in alpha lookup and cleanup), which can be narrowed to specific exception types to avoid swallowing unexpected errors.

### Resource Management Assessment
- **Strengths**: WindowVisuals.visualize introduces cleanup_and_close, closes figures via pyplot.close('all'), and recursively destroys canvases; figures are saved before embedding. File writes use context managers in main.py and WindowGenDZN.py.
- **Areas for improvement**: A few generic try/except cleanup blocks exist; adding finally blocks and narrowing exceptions would further strengthen resource safety.

### Architecture Assessment
- **Current state**: main.py still orchestrates UI events, file dialogs, process execution, and state; logic is distributed across UI modules. No separate model/controller modules with testable boundaries yet.
- **Next steps**: Extract MiniZinc runner, file operations, and data validation into separate modules.

## How to Update This File

This progress tracking file should be updated after each significant change or batch of changes to reflect the current status of development tasks.

**Status Values:**
- `Not done` - Task not started
- `Partially done` - Task in progress or partially completed
- `Done (partial)` - Task mostly complete but may need refinement
- `Done` - Task fully completed

---

*Last updated: October 16, 2025 (after code analysis)*
