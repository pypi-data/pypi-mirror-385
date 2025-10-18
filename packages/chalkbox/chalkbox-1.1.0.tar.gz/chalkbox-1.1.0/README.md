<p align="center">
  <img src="https://raw.githubusercontent.com/bulletinmybeard/chalkbox/refs/heads/master/docs/images/chalkbox-logo.png" alt="ChalkBox Logo">
</p>

<p align="center">
    <em>A batteries-included CLI UI kit on top of Rich</em>
</p>

[![CI](https://github.com/bulletinmybeard/chalkbox/workflows/CI/badge.svg)](https://github.com/bulletinmybeard/chalkbox/actions)
[![PyPI](https://img.shields.io/pypi/v/chalkbox?color=blue)](https://pypi.org/project/chalkbox/)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/poetry-managed-blue.svg)](https://python-poetry.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checking: mypy](https://img.shields.io/badge/type%20checking-mypy-blue.svg)](https://github.com/python/mypy)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Built on Rich](https://img.shields.io/badge/built%20on-Rich-009485.svg)](https://github.com/Textualize/rich)

A batteries-included CLI UI kit built on top of [Rich](https://github.com/Textualize/rich). ChalkBox provides consistent, themed, and composable components for building beautiful command-line interfaces with fail-safe defaults.

![ChalkBox Demo](https://raw.githubusercontent.com/bulletinmybeard/chalkbox/refs/heads/master/docs/images/hero-demo.gif)

## Why ChalkBox?

**ChalkBox = Rich + Batteries Included + Fail-Safe + Smart Defaults**

While [Rich](https://github.com/Textualize/rich) provides excellent terminal primitives, ChalkBox gives you production-ready components with graceful error handling, universal compatibility, and beautiful defaults out of the box.

## Installation

```bash
pip install chalkbox
```

## Quick Start

```python
from chalkbox import get_console, Spinner, Alert, Table
import time

console = get_console()

# Spinner with success/error states
with Spinner("Loading data") as spinner:
    time.sleep(2)
    spinner.success("Data loaded!")

# Severity-based alerts (6 levels: debug, info, success, warning, error, critical)
console.print(Alert.debug("Verbose mode enabled"))
console.print(Alert.info("Processing 1,234 records"))
console.print(Alert.success("Deployment complete"))
console.print(Alert.warning("API rate limit: 850/1000"))
console.print(Alert.error("Connection failed", details="Check network settings"))
console.print(Alert.critical("System shutdown in 60s", details="Save all work immediately"))

# Tables with severity styling
table = Table(headers=["Service", "Status", "Response Time"], row_styles="severity")
table.add_row("API", "✓ Running", "45ms", severity="success")
table.add_row("Cache", "⚠ Degraded", "230ms", severity="warning")
table.add_row("Queue", "✗ Down", "timeout", severity="error")
console.print(table)
```

## Key Features

- **Fail-Safe Design** - Graceful error handling with automatic fallbacks
- **Batteries Included** - Common patterns pre-built (alerts, spinners, steppers, etc.)
- **Auto Secret Masking** - Automatically masks passwords, keys, tokens
- **Non-TTY Support** - Works in CI/CD, Docker, piped output
- **Live Dashboards** - Real-time monitoring with terminal resize support
- **Theming System** - Consistent styling via config/env/code
- **Context Managers** - Clean resource handling for all stateful components

## Components

### Display & Content

| Component     | Description                                                         |
| :------------ | :------------------------------------------------------------------ |
| **Alert**     | 6-level severity alerts (debug/info/success/warning/error/critical) |
| **Table**     | Auto-sizing tables with severity-based row styling                  |
| **Section**   | Organized content containers with optional subtitles                |
| **CodeBlock** | Syntax-highlighted code display with file reading support           |
| **JsonView**  | JSON data visualization with pretty printing                        |
| **Markdown**  | Markdown rendering component                                        |
| **KeyValue**  | Key-value displays with automatic secret masking                    |
| **Tree**      | Hierarchical data visualization with file system support            |

### Progress & Status

| Component    | Description                                               |
| :----------- | :-------------------------------------------------------- |
| **Spinner**  | Loading indicators with success/fail/warning states       |
| **Progress** | Multi-task progress bars with ETA and thread-safe updates |
| **Status**   | Non-blocking status indicators for background operations  |
| **Stepper**  | Multi-step workflow tracking with status indicators       |

### Layout & Structure

| Component        | Description                                        |
| :--------------- | :------------------------------------------------- |
| **MultiPanel**   | Complex layouts with grids and dashboards          |
| **ColumnLayout** | Responsive column layouts with equal/custom sizing |
| **Divider**      | Section dividers with multiple styles              |
| **Align**        | Content alignment (horizontal & vertical)          |
| **Padding**      | Theme-aware spacing wrapper with multiple patterns |
| **Bar**          | Horizontal bar charts and metrics visualization    |

### Interactive Input

| Component      | Description                         |
| :------------- | :---------------------------------- |
| **Input**      | Text input with validation          |
| **IntInput**   | Integer input with range validation |
| **FloatInput** | Float input with range validation   |
| **Select**     | Choice selection from list          |
| **Confirm**    | Yes/no confirmation prompts         |

<details>

<summary><b>View code examples for common components</b></summary>

### Alert - Severity-based notifications

```python
from chalkbox import Alert, get_console

console = get_console()

# 6 severity levels with automatic styling
console.print(Alert.debug("Verbose mode enabled"))
console.print(Alert.info("Processing 1,234 records"))
console.print(Alert.success("Deployment complete!"))
console.print(Alert.warning("API rate limit: 85% used"))
console.print(Alert.error("Connection failed", details="Check network settings"))
console.print(Alert.critical("System shutdown in 60s", details="Save all work"))
```

### Spinner - Loading indicators

```python
from chalkbox import Spinner
import time

# Context manager with automatic cleanup
with Spinner("Loading data") as spinner:
    time.sleep(2)
    spinner.success("Data loaded!")

# Or show errors
with Spinner("Connecting to database") as spinner:
    try:
        # connection logic
        spinner.success("Connected!")
    except Exception:
        spinner.error("Connection failed!")
```

### Table - Structured data with severity styling

```python
from chalkbox import Table, get_console

console = get_console()
table = Table(headers=["Service", "Status", "Uptime"], row_styles="severity")

# Severity determines row color (success=green, warning=yellow, error=red)
table.add_row("API Gateway", "Running", "99.9%", severity="success")
table.add_row("Cache", "Degraded", "85.2%", severity="warning")
table.add_row("Message Queue", "Down", "0%", severity="error")

console.print(table)
```

### Progress - Multi-task tracking

```python
from chalkbox import Progress
import time

# Track multiple tasks with ETA
with Progress() as progress:
    task1 = progress.add_task("Building", total=100)
    task2 = progress.add_task("Testing", total=50)
    task3 = progress.add_task("Deploying", total=25)

    for i in range(100):
        progress.update(task1, advance=1)
        if i < 50:
            progress.update(task2, advance=1)
        if i < 25:
            progress.update(task3, advance=1)
        time.sleep(0.01)
```

### KeyValue - Configuration display with secret masking

```python
from chalkbox import KeyValue, get_console

console = get_console()
kv = KeyValue(title="System Configuration")

kv.add("Region", "us-east-1")
kv.add("Environment", "production")
kv.add("API URL", "https://api.example.com")
kv.add("API Key", "sk-1234567890abcdef")        # Automatically masked as "sk******ef"
kv.add("Database Password", "super_secret_123") # Automatically masked

console.print(kv)
```

### Stepper - Workflow tracking with mixed states

```python
from chalkbox import Stepper, get_console

console = get_console()
stepper = Stepper()

stepper.add_step("Initialize environment")
stepper.add_step("Install dependencies")
stepper.add_step("Run migrations")
stepper.add_step("Deploy application")
stepper.add_step("Run health checks")

# Update step statuses
stepper.complete(0)  # ● Initialize environment
stepper.complete(1)  # ● Install dependencies
stepper.fail(2)      # ✖ Run migrations (failed!)
stepper.skip(3)      # ⊘ Deploy application (skipped due to failure)
stepper.skip(4)      # ⊘ Run health checks (skipped)

console.print(stepper)
```

**Explore more examples:** [`demos/components/`](https://github.com/bulletinmybeard/chalkbox/tree/main/demos/components) | [`demos/showcases/`](https://github.com/bulletinmybeard/chalkbox/tree/main/demos/showcases)

</details>

## Theming

Customize ChalkBox colors and glyphs by creating `~/.chalkbox/theme.toml`:

```toml
[colors]
primary = "cyan"
success = "green"
warning = "yellow"
error = "red"
info = "blue"

[glyphs]
success = "✓"
error = "✗"
warning = "⚠"
info = "ℹ"

[spacing]
default = 1
section = 2

[borders]
default = "rounded"
```

You can also set theme values via environment variables using the pattern:

```bash
CHALKBOX_THEME_<CATEGORY>_<KEY>=<VALUE>
```

**Examples:**

```bash
export CHALKBOX_THEME_COLORS_PRIMARY=magenta
export CHALKBOX_THEME_GLYPHS_SUCCESS="[OK]"
export CHALKBOX_THEME_SPACING_DEFAULT=2
export CHALKBOX_THEME_BORDERS_STYLE=heavy
```

<details>

<summary><b>View all available environment variables</b></summary>

### Colors (12 variables)

```bash
CHALKBOX_THEME_COLORS_PRIMARY=cyan
CHALKBOX_THEME_COLORS_SECONDARY=blue
CHALKBOX_THEME_COLORS_SUCCESS=green
CHALKBOX_THEME_COLORS_WARNING=yellow
CHALKBOX_THEME_COLORS_ERROR=red
CHALKBOX_THEME_COLORS_INFO=blue
CHALKBOX_THEME_COLORS_MUTED="dim white"
CHALKBOX_THEME_COLORS_ACCENT=bright_cyan
CHALKBOX_THEME_COLORS_BACKGROUND=default
CHALKBOX_THEME_COLORS_TEXT=default
CHALKBOX_THEME_COLORS_DEBUG="dim cyan"
CHALKBOX_THEME_COLORS_CRITICAL=bright_red
```

### Glyphs (16 variables)

```bash
CHALKBOX_THEME_GLYPHS_SUCCESS=✓
CHALKBOX_THEME_GLYPHS_ERROR=✖
CHALKBOX_THEME_GLYPHS_WARNING=⚠
CHALKBOX_THEME_GLYPHS_INFO=i
CHALKBOX_THEME_GLYPHS_DEBUG=▪
CHALKBOX_THEME_GLYPHS_CRITICAL=‼
CHALKBOX_THEME_GLYPHS_ARROW=→
CHALKBOX_THEME_GLYPHS_BULLET=•
CHALKBOX_THEME_GLYPHS_CHECK=✓
CHALKBOX_THEME_GLYPHS_CROSS=✖
CHALKBOX_THEME_GLYPHS_SPINNER="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
CHALKBOX_THEME_GLYPHS_PENDING=○
CHALKBOX_THEME_GLYPHS_RUNNING=◔
CHALKBOX_THEME_GLYPHS_COMPLETE=●
CHALKBOX_THEME_GLYPHS_FAILED=✖
CHALKBOX_THEME_GLYPHS_SKIPPED=⊘
```

### Spacing (6 variables)

```bash
CHALKBOX_THEME_SPACING_XS=0
CHALKBOX_THEME_SPACING_SM=1
CHALKBOX_THEME_SPACING_DEFAULT=1
CHALKBOX_THEME_SPACING_MD=2
CHALKBOX_THEME_SPACING_LG=3
CHALKBOX_THEME_SPACING_XL=4
```

### Borders (4 variables)

```bash
CHALKBOX_THEME_BORDERS_STYLE=rounded
CHALKBOX_THEME_BORDERS_PANEL=rounded
CHALKBOX_THEME_BORDERS_TABLE=rounded
CHALKBOX_THEME_BORDERS_SECTION=rounded
```

**Valid border styles:** `rounded`, `heavy`, `double`, `square`, `ascii`

</details>

Or programmatically in your code:

```python
from chalkbox import set_theme

# Set individual values
set_theme({
    "colors.primary": "magenta",
    "colors.success": "bright_green",
})

# Or load a custom theme file
from chalkbox.core.theme import Theme
from pathlib import Path

custom_theme = Theme.from_file(Path("~/.chalkbox/theme-dark.toml").expanduser())
set_theme(custom_theme)
```

## Examples

See the [demos directory on GitHub](https://github.com/bulletinmybeard/chalkbox/tree/main/demos) for examples including component demos, real-world showcases, and workflow simulations.

## Documentation

**Full documentation site coming soon!** For now, explore the many examples in https://github.com/bulletinmybeard/chalkbox/demos/.

## ChalkBox vs Rich

ChalkBox is built **on top of** Rich, not as a replacement:

| Feature            | Rich                 | ChalkBox                  |
| ------------------ | -------------------- | ------------------------- |
| **Fail-Safe**      | Can raise exceptions | Handles errors gracefully |
| **Patterns**       | Low-level primitives | High-level components     |
| **Configuration**  | Manual styling       | Smart defaults + theming  |
| **Secret Masking** | Manual               | Automatic                 |
| **Non-TTY**        | Manual handling      | Automatic                 |

**Use ChalkBox when:** Building CLI tools, need consistency, want fail-safe components
**Use Rich when:** Need maximum flexibility, building custom visuals, library development

**Mix both freely!** ChalkBox components return Rich renderables:

```python
from chalkbox import Alert
from rich.panel import Panel
from rich.console import Console

console = Console()
panel = Panel(Alert.success("Done!"), title="Status")
console.print(panel)
```

## Requirements

- Python 3.12+
- Rich >= 14.2.0

**Why Python 3.12+?** ChalkBox uses modern Python features for clean code and better type hints.

## Contributing

I welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup and workflow
- Coding standards and best practices
- How to submit pull requests
- Testing and quality checks

## License

MIT License - see [LICENSE](LICENSE) file for details.

ChalkBox is built on [Rich](https://github.com/Textualize/rich) by [Textualize](https://www.textualize.io/), also MIT licensed.

## Credits

- **Author**: Robin Schulz ([@bulletinmybeard](https://github.com/bulletinmybeard))
- **Built on**: [Rich](https://github.com/Textualize/rich) by Will McGugan
- **Inspired by**: [Chalk](https://github.com/chalk/chalk), [Inquirer](https://github.com/SBoudrias/Inquirer.js)
