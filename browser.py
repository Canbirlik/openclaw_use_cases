"""
🤖 AI AGENT INSTRUCTIONS (READ CAREFULLY):
------------------------------------------
This script leverages Playwright to control a Chromium browser, enabling web content reading or screenshots.
For reliable operation, especially when sharing with other agents, follow these detailed setup steps.

IMPORTANT: Running with `--visible` (non-headless mode) REQUIRES an XServer (graphical environment).
If you are in a terminal-only environment (e.g., WSL without GUI, SSH without X11 forwarding),
DO NOT use `--visible` or ensure `xvfb-run` is configured if you must see the UI.
Otherwise, run in HEADLESS mode (default behavior when `--visible` is omitted).

SETUP VIRTUAL ENVIRONMENT & INSTALL DEPENDENCIES:
------------------------------------------------
Execute the following commands in order, from the directory where `browser.py` is located:

1.  CREATE VIRTUAL ENVIRONMENT:
    openclaw exec --command "python3 -m venv venv-browser" --workdir "."

2.  ACTIVATE VIRTUAL ENVIRONMENT & INSTALL PYTHON PACKAGES (`playwright`):
    openclaw exec --command "source venv-browser/bin/activate && pip install playwright" --workdir "."

3.  INSTALL BROWSER BINARIES (`chromium`):
    openclaw exec --command "source venv-browser/bin/activate && playwright install chromium" --workdir "."

4.  (IF ON LINUX AND ENCOUNTERING LIBRARY ERRORS) INSTALL SYSTEM LIBRARIES:
    If you encounter errors like "libnspr4.so", "libnss3.so", or "libasound.so.2" missing,
    you will need to install these system libraries. This typically requires `sudo` access.
    
    Execute these commands in your TERMINAL (not via OpenClaw exec, due to elevated permissions):
    sudo apt-get update
    sudo apt-get install -y libnspr4 libnss3 libasound2t64  # Note: libasound2t64 for newer Ubuntu

HOW TO RUN THE TOOL:
--------------------
Once the setup is complete, use the python interpreter inside the virtual environment.
Always execute from the directory where `browser.py` is located (using `--workdir "."`).

EXAMPLE USAGE (to read GitHub Trending, HEADLESS mode):
   openclaw exec --command "source venv-browser/bin/activate && ./venv-browser/bin/python browser.py --url \"https://github.com/trending\" --action read" --workdir "."

EXAMPLE USAGE (to take a screenshot of a Twitter profile, HEADLESS mode):
   openclaw exec --command "source venv-browser/bin/activate && ./venv-browser/bin/python browser.py --url \"https://twitter.com/elonmusk\" --action screenshot" --workdir "."

FLAGS:
   --url <URL>      : URL to visit (required)
   --action <read|screenshot> : Action to perform (default: read)
   --visible        : Force the browser to show on screen (Headless=False, requires XServer)

"""

import argparse
import sys
import time
from playwright.sync_api import sync_playwright

def browse(url, action, visible=False):
    print(f"\n🌍 INITIALIZING BROWSER AGENT...")
    print(f"🎯 TARGET: {url}")
    print(f"👀 MODE: {'VISIBLE' if visible else 'HEADLESS'}")
    
    with sync_playwright() as p:
        # slow_mo=1000 for visibility in video/demonstrations
        # viewport={'width': 1280, 'height': 720} provides a consistent screen size
        browser = p.chromium.launch(headless=not visible, slow_mo=1000)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()
        
        try:
            print("🚀 Navigating to page...")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Give some extra time for dynamic content to load after DOMContentLoaded
            time.sleep(2)

            if action == "read":
                print("📖 Reading content...")
                title = page.title()
                
                # Extract only the body text and clean it up
                content = page.evaluate("document.body.innerText")
                # Limit to first 5000 characters for conciseness and context window limits
                clean_content = ' '.join(content.split())[:5000] 
                
                print(f"\n{'='*20} PAGE REPORT {'='*20}")
                print(f"TITLE: {title}")
                print(f"SUMMARY:\n{clean_content}...")
                print(f"{'='*50}\n")

            elif action == "screenshot":
                filename = "evidence.png"
                page.screenshot(path=filename)
                print(f"📸 Screenshot captured: {filename}")

        except Exception as e:
            print(f"❌ BROWSER ERROR: {e}")
        finally:
            print("🔒 Closing browser session.")
            browser.close()

def main():
    parser = argparse.ArgumentParser(description="AI Browser Tool using Playwright")
    parser.add_argument("--url", required=True, help="URL to visit")
    parser.add_argument("--action", choices=["read", "screenshot"], default="read", help="Action to perform (read or screenshot)")
    parser.add_argument("--visible", action="store_true", help="Show browser UI (requires XServer)")
    
    args = parser.parse_args()
    
    browse(args.url, args.action, visible=args.visible)

if __name__ == "__main__":
    main()
