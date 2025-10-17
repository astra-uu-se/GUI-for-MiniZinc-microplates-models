# MPLACE Progress Tracking

This document tracks the progress of key tasks in the MPLACE project.

## Current Status

| Priority | Item                             | Status         | Details                                                                                      |
|----------|----------------------------------|----------------|----------------------------------------------------------------------------------------------|
| High     | Implement MVC Architecture       | Not done       | UI, logic, and I/O are tightly coupled across main.py, WindowGenDZN.py, and WindowVisuals.py; need to separate Model (data structures), View (UI components), and Controller (business logic) layers. |
| High     | Decouple Window Dependencies     | Done           | Replaced direct variable sharing between main and WindowGenDZN with callback-based communication; introduced DznGenerationResult dataclass for structured data transfer; WindowGenDZN now uses completion_callback instead of directly manipulating main window variables; clean separation of concerns achieved. |
| High     | Add Comprehensive Error Handling | Done           | All generic except: blocks replaced with specific exceptions (ValueError, TypeError, KeyError, etc.); proper exception chaining with 'from e' added; user-friendly error dialogs implemented throughout all modules. |
| High     | Improve Resource Management      | Done           | Context managers for all file operations; matplotlib figures properly closed with pyplot.close(fig); defensive error handling in plotting ensures figures freed on failure; UI state consistency maintained across error paths; subprocess handling preserved as tested and working. |
| Medium   | Add Input Validation Layer       | Done           | Comprehensive schema validation for compounds/controls dictionaries with parse_materials_dict(), validate_materials_schema(), validate_plate_dimensions(), and format_validation_errors() functions; validates structure, types, bounds (rows/cols ≥ 1), material names (≤100 chars, printable), replicate counts (≥1), and provides user-friendly multi-error messages with examples; replaces basic ast.literal_eval error catching. |
| Medium   | Configuration Management         | Partially done | paths.ini parsing centralized in utility.read_paths_ini_file with clearer error messages; needs environment variable support, validation schema, and centralized configuration object. Further improvements planned by original author. |
| Medium   | Code Style Standardization      | Done           | Comprehensive docstrings added to all functions with Args, Returns, Raises sections; consistent comment formatting throughout; proper type annotations on function parameters and returns. |
| Medium   | Add Comprehensive Type Hints    | Done           | Complete type annotations added across all modules using typing imports (List, Dict, Tuple, Union, Sequence); function signatures, class attributes, and global variables properly typed; numpy arrays and complex generic types annotated. |
| Medium   | Implement Consistent Naming Conventions | Done        | Constants converted to UPPERCASE (LETTERS_CAPITAL, LETTERS_LOWERCASE); variables use descriptive names (drugs, controls, num_rows, num_cols); UI elements follow consistent snake_case naming; preserved COMPD tool-specific naming. |
| Medium   | Extract Constants and Magic Numbers | Done        | Comprehensive constants.py module with organized classes (PlateDefaults, UI, Visualization, Performance, PathsIni, Messages, WindowConfig, MaterialDefaults, FileTypes, Validation, System); extracted 60+ magic numbers including plate dimensions, UI padding, widget sizes, visualization parameters, path parsing strings/offsets, and default values; significantly improved maintainability. |
| Medium   | **Separate UI Layout from Logic**    | **In Progress** | **PRIORITY TASK: WindowGenDZN mixes UI setup with business logic; need clear separation between interface definition and data processing. See detailed reorganization plan below.** |
| Low      | Cache Coordinate Transformations | Done           | Added @lru_cache(maxsize=2048) decorator to transform_coordinate function in utility.py; provides significant performance improvement for repeated well coordinate processing across materials and layouts. |
| Low      | Precompute Alpha Mappings        | Done           | Precompute transform_concentrations_to_alphas once per material in draw_plates() and pass to draw_plate() and draw_material_scale(); eliminates repeated alpha calculation across layouts and significantly improves visualization performance for multi-layout datasets. |
| Low      | Replace Tab20 Colormap Limitation | Not done      | Current 20-color limit causes repetition with many materials; implement extended colormap with 50+ distinct colors for better material differentiation. |
| Low      | Optimize Matplotlib Performance  | Done           | Cached pyplot.get_cmap('tab20') at module level as COLORMAP_TAB20 in WindowVisuals.py; eliminates repeated colormap lookups and improves rendering performance. |
| Low      | Implement Logging Framework     | Done           | Comprehensive logging system with dual approach: preserved print() statements for user-visible feedback while adding structured logging for debugging. PNG save paths now logged and printed for user visibility. Log file (mplace.log) captures all operations with timestamps. Logging levels: DEBUG for technical details, INFO for major operations, WARNING for recoverable issues, ERROR for failures. |
| Low      | Add Progress Indicators          | Not done       | Long-running MiniZinc operations show minimal feedback; add progress bars and status updates for better user experience. |
| Low      | Improve Error Diagnostics        | Not done       | MiniZinc failures could provide more specific diagnostic information; enhance subprocess error handling with context-specific guidance. |
| Low      | Add Bounds Checking             | Not done       | Plate dimensions and layout parameters lack validation against reasonable limits; add input validation with helpful error messages. |
| Low      | Enhance Documentation           | Not done       | Complex algorithms like parse_control_string need more detailed inline comments; add concrete usage examples in docstrings. |
| Low      | Add Unit Test Coverage          | Not done       | No apparent test coverage for utility functions and data processing; create test suite for core functionality. |
| Low      | Add Integration Tests           | Not done       | No end-to-end testing of DZN → MiniZinc → CSV → Visualization workflow; add comprehensive integration test suite. |
| Low      | Add Keyboard Shortcuts          | Not done       | No keyboard shortcuts for common operations; add standard shortcuts (Ctrl+O for open, etc.) for improved productivity. |
| Low      | Create Recent Files Menu        | Not done       | No quick access to recently used DZN/CSV files; add recent files functionality for better workflow efficiency. |
| Low      | Add Batch Processing Support    | Not done       | No support for processing multiple files in sequence; add batch processing capabilities for research workflows. |
| Low      | Expand Export Format Options    | Not done       | Only PNG export currently supported; add PDF, SVG support for publication-quality figures. |
| Low      | Add Data Consistency Validation | Not done       | No validation that CSV data matches expected DZN parameters; add cross-validation between input and output data. |
| Low      | Create Data Transfer Objects    | Not done       | Complex parameter passing could use structured objects instead of individual parameters for better maintainability. |

---

## DETAILED REORGANIZATION PLAN: "Separate UI Layout from Logic"

*This section provides the step-by-step implementation plan for the priority task of separating UI and business logic.*

### Current Issues Analysis

**WindowGenDZN.py - Severe Separation Issues:**
- `generate_dzn_file()` function (150+ lines) combines complex data processing, validation, file generation, AND UI management
- Data processing, validation logic, and DZN text generation embedded in UI code
- Business logic tightly coupled with Tkinter event handlers

**Main.py - Moderate Issues:**
- Functions like `run_minizinc()` handle both UI state management AND business logic
- File I/O operations directly embedded in UI event handlers
- CSV text extraction and DZN parameter parsing mixed with UI updates

**WindowVisuals.py - Good Separation:**
- Already has decent separation between visualization logic and UI layout
- Minor improvements possible but not critical

### Target File Organization

```
mplace/
├── mplace.py                 # Renamed from main.py
├── ui/                       # UI windows only
│   ├── __init__.py           # Empty file  
│   ├── window_dzn.py         # Renamed from WindowGenDZN.py
│   └── window_visuals.py     # Renamed from WindowVisuals.py
├── core/                     # Logic helpers and processing
│   ├── __init__.py           # Empty file
│   ├── dzn_writer.py         # NEW - DZN text generation logic
│   ├── minizinc_runner.py    # NEW - MiniZinc subprocess handling  
│   └── io_utils.py           # NEW - File operations
├── models/                   # Data structures and constants
│   ├── __init__.py           # Empty file
│   ├── constants.py          # Moved from root
│   └── dto.py                # NEW - Data classes
├── config/                   # Configuration management
│   ├── __init__.py           # Empty file
│   ├── paths.ini             # Moved from root
│   └── loader.py             # NEW - Configuration loading (the need is to be explored)
├── mzn/                      # MiniZinc model files
│   ├── plate-design.mzn      # Moved from root
│   ├── layout_predicates.mzn # Moved from root  
│   ├── plaid_default.mpc     # Moved from root
│   └── compd_default.mpc     # Moved from root
├── tools/                    # User helper files
│   └── Convert the compounds and controls.xlsx
├── utility.py                # Keep temporarily, migrate gradually
├── README.md, PROGRESS.md, LICENSE  # Unchanged
```

### Implementation Stages (timeline is very approximate)

#### Stage 1: Create Package Structure (Week 1, Days 1-2)
- **Objective**: Set up directory structure and move safe files
- **Tasks**:
  1. Create directories: `mkdir ui core models config mzn tools`
  2. Create empty `__init__.py` files: `touch ui/__init__.py core/__init__.py models/__init__.py config/__init__.py`
  3. Move non-code files:
     - `mv constants.py models/`
     - `mv paths.ini config/`
     - `mv *.mzn *.mpc mzn/`
     - `mv "Convert the compounds and controls.xlsx" tools/`
  4. Update imports for constants and test application still works

#### Stage 2: Rename Main Files (Week 1, Days 3-4)  
- **Objective**: Rename files to cleaner names and organize into packages
- **Tasks**:
  1. Rename files:
     - `mv main.py app.py`
     - `mv WindowGenDZN.py ui/window_dzn.py`
     - `mv WindowVisuals.py ui/window_visuals.py`
  2. Fix imports in `app.py`:
     - `import WindowGenDZN as wd` → `from ui import window_dzn as wd`
     - `import WindowVisuals as wv` → `from ui import window_visuals as wv`
     - `from constants import ...` → `from models.constants import ...`
  3. Fix imports in UI files for constants
  4. Test application works after renames

#### Stage 3: Extract File Operations (Week 1-2)
- **Objective**: Create core utilities for file handling
- **Tasks**:
  1. Create `core/io_utils.py`:
     - Move `read_csv_file()`, `path_show()` from utility.py
     - Add CSV writing helpers from UI files
  2. Create `config/loader.py`:
     - Move `read_paths_ini_file()` from utility.py  
     - Rename to `load_paths_config()` for clarity
  3. Update imports:
     - In app.py: `from utility import read_paths_ini_file` → `from config.loader import load_paths_config`
     - In UI files: `from utility import read_csv_file` → `from core.io_utils import read_csv_file`

#### Stage 4: Extract MiniZinc Logic (Week 2, Days 2-3)
- **Objective**: Separate subprocess handling from UI  
- **Tasks**:
  1. Create `core/minizinc_runner.py`:
     ```python
     class MiniZincRunner:
         def run_model(self, minizinc_path, solver_config, model_file, data_file):
             # Move run_cmd logic here

         def extract_csv_from_output(self, output_text):
             # Move extract_csv_text logic here
     ```
  2. Update `app.py` in `run_minizinc()` function:
     - Replace direct `run_cmd()` call with `MiniZincRunner` usage
     - Keep UI state management in app.py, move subprocess logic to core

#### Stage 5: Extract DZN Generation Logic (Week 2, Days 4-5) - **CRITICAL**
- **Objective**: Remove the biggest logic blob from UI
- **Tasks**:
  1. Create `core/dzn_writer.py`:
     ```python
     class DZNWriter:
         def generate_dzn_content(self, compounds_dict, controls_dict, form_params):
             # Move the big dzn_txt building logic from ui/window_dzn.py
             # Keep exact same algorithm, just extract it

         def _process_compounds(self, compounds_dict):
             # Move compound processing logic

         def _process_controls(self, controls_dict):
             # Move control processing logic  
     ```
  2. Update `ui/window_dzn.py` in `generate_dzn_file()`:
     ```python
     # Replace 100+ line dzn_txt building with:
     from core.dzn_writer import DZNWriter

     writer = DZNWriter()
     dzn_txt = writer.generate_dzn_content(compounds_dict, controls_dict, form_params)
     ```
  3. Keep validation logic in UI initially (can be moved later)

#### Stage 6: Create Data Classes (Week 3, Day 1)
- **Objective**: Formalize data transfer between layers
- **Tasks**:
  1. Create `models/dto.py`:
     - Move `DznGenerationResult` from ui/window_dzn.py
     - Add other simple data classes for parameter passing
  2. Update imports where `DznGenerationResult` is used

#### Stage 7: Clean Up & Finalize (Week 3, Days 2-3)
- **Objective**: Complete migration and verify everything works
- **Tasks**:
  1. Gradually empty `utility.py`:
     - Move remaining functions to appropriate core/ files  
     - When empty, delete utility.py
  2. Test everything works end-to-end
  3. Update this PROGRESS.md:
     - Mark "Separate UI Layout from Logic" as Done
     - Add notes about completed reorganization

### Organization Rules

**What Goes Where:**
- **ui/**: Only Tkinter widgets, layouts, and event binding. No file I/O, no complex algorithms
- **core/**: All the "heavy lifting" - file processing, subprocess calls, text generation  
- **models/**: Constants, simple data classes. No behavior/methods
- **config/**: Configuration loading and validation

**Safety Guidelines:**
- Test after each stage - don't move to next stage if current breaks
- Git commit after each working stage  
- One file at a time - don't move multiple files simultaneously
- Fix imports immediately - don't leave broken imports


## How to Update This File

This progress tracking file should be updated after each significant change or batch of changes to reflect the current status of development tasks.

**Status Values:**
- `Not done` - Task not started
- `Partially done` - Task in progress or partially completed  
- `In progress` - Task currently being worked on
- `Done (partial)` - Task mostly complete but may need refinement
- `Done` - Task fully completed

---

*Last updated: October 17, 2025 (added detailed reorganization plan for "Separate UI Layout from Logic" priority task)*
