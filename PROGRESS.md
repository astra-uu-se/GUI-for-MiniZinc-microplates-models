# MPLACE Progress Tracking

This document tracks the progress of key tasks in the MPLACE project.

## Current Status

| Priority | Item                             | Status         | Details                                                                                      |
|----------|----------------------------------|----------------|----------------------------------------------------------------------------------------------|
| High     | Implement MVC Architecture       | Not done yet   | UI, logic, and I/O are still coupled across main.py, WindowGenDZN.py, and WindowVisuals.py; no clear Model/View/Controller separation observed. |
| High     | Add Comprehensive Error Handling | Done           | All generic except: blocks replaced with specific exceptions (ValueError, TypeError, KeyError, etc.); proper exception chaining with 'from e' added; user-friendly error dialogs implemented throughout all modules. |
| High     | Improve Resource Management      | Done           | Context managers for all file operations; matplotlib figures properly closed with pyplot.close(fig); defensive error handling in plotting ensures figures freed on failure; UI state consistency maintained across error paths; subprocess handling preserved as tested and working. |
| Medium   | Code Style Standardization      | Done           | Comprehensive docstrings added to all functions with Args, Returns, Raises sections; consistent comment formatting throughout; proper type annotations on function parameters and returns. |
| Medium   | Add Comprehensive Type Hints    | Done           | Complete type annotations added across all modules using typing imports (List, Dict, Tuple, Union, Sequence); function signatures, class attributes, and global variables properly typed; numpy arrays and complex generic types annotated. |
| Medium   | Implement Consistent Naming Conventions | Done        | Constants converted to UPPERCASE (LETTERS_CAPITAL, LETTERS_LOWERCASE); variables use descriptive names (drugs, controls, num_rows, num_cols); UI elements follow consistent snake_case naming; preserved COMPD tool-specific naming. |
| Medium   | Configuration Management         | Partially done | paths.ini parsing centralized in utility.read_paths_ini_file with clearer error messages; still no dedicated config module or validation schema; GUI holds configuration state. Further improvements planned by original author. |
| Low      | Performance Optimizations       | Not done       | No apparent performance-specific work; visualization likely fine for typical plate sizes; no caching or vectorization beyond basic numpy usage. |
| Low      | Enhanced User Experience         | Not done       | Core flows functional; user messages improved on errors; no UX enhancements like progress indicators beyond simple labels; fixed save paths for PNG still a limitation. Replace 'tab20' colormap with a colormap with a larger number (50+) of distinct colors. |


## How to Update This File

This progress tracking file should be updated after each significant change or batch of changes to reflect the current status of development tasks.

**Status Values:**
- `Not done` - Task not started
- `Partially done` - Task in progress or partially completed  
- `Done (partial)` - Task mostly complete but may need refinement
- `Done` - Task fully completed

---

*Last updated: October 16, 2025 (reverted configuration management to partially done; added colormap enhancement to UX)*
