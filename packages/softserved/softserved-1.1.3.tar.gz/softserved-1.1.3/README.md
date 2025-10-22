# softserved

A lightweight, stylish local web server for serving static files from your terminal. Perfect for quick demos, prototyping, and development workflows.

## Quick Start

```bash
pip install -e .
softserved
```

Done. Your browser opens at `http://localhost:8000` and you're serving.

## Why softserved?

Just a static server. No fluff. `softserved` is a cli-based tool for watching vanilla html/css/js projects.

## Features

**Clean, minimal CLI** — Starts a server in one command  
**Multiple styling themes** — default, dark, and mono options  
**Live reload** — Auto-refresh browser when files change  
**Lightweight** — No bloat, just Python stdlib + colorama  
**Auto-opens browser** — (optional) Opens your default browser automatically  
**Flexible directory serving** — Serve any folder, any port

![softserved demo](screenshots/demo.png)
![Bye Bye softserved demo](screenshots/demo_2.png)

## Installation

### From GitHub

```bash
git clone https://github.com/tolaoyelola/softserved.git
cd softserved
pip install -r requirements.txt
pip install -e .
```

### Verify Installation

```bash
softserved --help
```

## Usage

### Basic Examples

```bash
# Serve current directory on port 8000
softserved

# Serve with custom port and directory
softserved -p 9001 -d ./my-site

# Enable live reload
softserved --reload

# Don't auto-open browser
softserved --no-browser

# Use dark theme for dark terminals
softserved --style dark

# No colors (mono)
softserved --style mono

# Combine options
softserved -p 8080 -d ./portfolio --reload --style dark
```

### Available Options

| Option         | Default | Description                                  |
| -------------- | ------- | -------------------------------------------- |
| `-p, --port`   | 8000    | Port to serve on                             |
| `-d, --dir`    | `.`     | Directory to serve                           |
| `--no-browser` | false   | Don't auto-open browser                      |
| `--reload`     | false   | Enable live reload (requires watchdog)       |
| `--style`      | default | Terminal theme: `default`, `dark`, or `mono` |

## Requirements

**Core dependencies:**

- Python 3.6+
- `colorama` — for colored terminal output

**Optional dependencies:**

- `watchdog` — for live reload functionality

Install all:

```bash
pip install -r requirements.txt
```

## How It Works

1. **Server** — Uses Python's built-in `SimpleHTTPRequestHandler`
2. **Styling** — Colorama handles cross-platform terminal colors
3. **Live Reload** — Watchdog monitors file changes and triggers browser refresh

## Troubleshooting

**"Port already in use"**

```bash
softserved -p 8001  # Use a different port
```

**"watchdog not installed"**

```bash
pip install watchdog
```

**Browser won't open**

```bash
softserved --no-browser  # Disable auto-open
# Then manually navigate to http://localhost:8000
```

**Stop the server**

```bash
Press Ctrl+C to gracefully shut down
```

## Contributing

Contributions welcome! Feel free to open issues or submit PRs.

## License

MIT — See LICENSE file for details.
