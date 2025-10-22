#!/usr/bin/env python3
"""
softserved — lightweight local web server for terminals with styling options.

Usage:
  softserved [-p PORT] [-d DIR] [--no-browser] [--reload] [--style STYLE]

Examples:
  softserved
      Starts server on port 8000 serving current directory, opens your browser.

  softserved --no-browser
      Runs the server quietly without opening a browser tab.

  softserved --reload
      Enables auto-reload: the browser refreshes automatically when files change.

  softserved -p 8080 -d ./portfolio --reload
      Serves your 'portfolio' folder on port 8080 with live reload.

  softserved --style dark
      Uses a darker banner theme for terminal readability.

Styling Options:
  --style [default|dark|mono]
      Choose how the banner and logs are displayed:
      - default: colorful and bright
      - dark: muted tones for dark terminals
      - mono: minimal, no colors (for plain terminals)
"""

import http.server
import socketserver
import os
import sys
import argparse
import webbrowser
from colorama import Fore, Style, init

init(autoreset=True)

# ======================================================================
# BANNER TEMPLATES
# ======================================================================

BANNERS = {
    "default": f"""
{Fore.BLUE}{Style.BRIGHT}
  ╔═══════════════════════════════════════════════════════════════════╗
                        🍦 softserved v1.1 🍦               
        Simple, stylish, and surprisingly handy static file server
  ╚═══════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
""",
    "dark": f"""
{Fore.CYAN}{Style.DIM}
  ┌───────────────────────────────────────────────────────────────────┐
      softserved v1.1 — Sleek static file server for dark terminals
  └───────────────────────────────────────────────────────────────────┘
{Style.RESET_ALL}
""",
    "mono": """
  ===========================================================
    softserved v1.1 — Simple static file server (no styling)
  ===========================================================
"""
}

# ======================================================================
# LOG HELPERS
# ======================================================================

def print_info(msg, style="default"):
    if style == "mono":
        print(f"[INFO] {msg}")
    else:
        print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} {msg}")

def print_warn(msg, style="default"):
    if style == "mono":
        print(f"[WARN] {msg}")
    else:
        print(f"{Fore.YELLOW}[WARN]{Style.RESET_ALL} {msg}")

def print_error(msg, style="default"):
    if style == "mono":
        print(f"[ERROR] {msg}")
    else:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}")

# ======================================================================
# SERVER LOGIC
# ======================================================================

def serve(directory=".", port=8000, open_browser=True, watch_reload=False, style="default"):
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", port), handler) as httpd:
        print(BANNERS.get(style, BANNERS["default"]))
        print_info(f"Serving from: {os.path.abspath(directory)}", style)
        print_info(f"Server started on port {port}", style)
        print_info(f"URL: http://localhost:{port}", style)

        if watch_reload:
            print_info("Live reload: ENABLED", style)
        else:
            print_warn("Live reload: disabled (use --reload to enable)", style)

        print_info("Press Ctrl+C to stop the server", style)
        print()

        if open_browser:
            webbrowser.open(f"http://localhost:{port}")

        # ------------------------------------------------------------------
        # WATCHDOG (optional)
        # ------------------------------------------------------------------
        if watch_reload:
            try:
                from watchdog.observers import Observer
                from watchdog.events import FileSystemEventHandler
            except ImportError:
                print_warn("Watchdog not installed. Run `pip install watchdog` for auto-reload.", style)
                httpd.serve_forever()
                return

            class ReloadHandler(FileSystemEventHandler):
                def on_any_event(self, event):
                    if not event.is_directory:
                        print_info("File change detected. Reloading browser...", style)
                        webbrowser.open(f"http://localhost:{port}", new=0, autoraise=True)

            observer = Observer()
            observer.schedule(ReloadHandler(), ".", recursive=True)
            observer.start()

        # ------------------------------------------------------------------
        # MAIN LOOP
        # ------------------------------------------------------------------
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n" + Fore.CYAN + "Shutting down server... Bye 👋" + Style.RESET_ALL)
        finally:
            if watch_reload:
                observer.stop()
                observer.join()

# ======================================================================
# ENTRY POINT
# ======================================================================

def main():
    parser = argparse.ArgumentParser(description="Serve a folder with style.")
    parser.add_argument("-p", "--port", type=int, default=8000, help="Port to serve on (default: 8000)")
    parser.add_argument("-d", "--dir", default=".", help="Directory to serve (default: current directory)")
    parser.add_argument("--no-browser", action="store_true", help="Don't auto-open the browser")
    parser.add_argument("--reload", action="store_true", help="Enable live reload when files change")
    parser.add_argument("--style", choices=["default", "dark", "mono"], default="default", help="Choose terminal style (default: colorful)")
    args = parser.parse_args()

    serve(
        directory=args.dir,
        port=args.port,
        open_browser=not args.no_browser,
        watch_reload=args.reload,
        style=args.style
    )

if __name__ == "__main__":
    main()