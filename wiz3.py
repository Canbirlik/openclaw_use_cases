"""
🤖 AI AGENT INSTRUCTIONS FOR WIZ LIGHT:
------------------------------------------------
To use this script reliably, especially in environments with Python's PEP 668
(externally-managed-environment) enforcement, it is highly recommended to set
up and run it within a Python Virtual Environment.

This script is designed to be highly portable. The IP address for the bulb is
always passed as a command-line argument. The following instructions assume
you are running the commands from the directory where `wiz3.py` is located.

FOLLOW THESE STEPS TO SET UP AND RUN:

1.  CREATE A VIRTUAL ENVIRONMENT (if not already in one):
    Execute this command in the *current directory* where wiz3.py is located:
    openclaw exec --command "python3 -m venv venv" --workdir "."

2.  INSTALL DEPENDENCIES IN THE VIRTUAL ENVIRONMENT:
    Execute this command in the *current directory*:
    openclaw exec --command "source venv/bin/activate && pip install pywizlight" --workdir "."

3.  RUN THE SCRIPT USING THE VIRTUAL ENVIRONMENT'S PYTHON:
    Once the virtual environment is set up and dependencies are installed,
    you can run the script.

    EXAMPLE USAGE (to start disco mode at 192.168.1.109 for 60 seconds):
    openclaw exec --command "source venv/bin/activate && python3 wiz3.py --ip 192.168.1.109 --action disco --duration 60" --workdir "."

    Other actions:
    - Turn ON:
      openclaw exec --command "source venv/bin/activate && python3 wiz3.py --ip 192.168.1.109 --action on" --workdir "."
    - Turn OFF:
      openclaw exec --command "source venv/bin/activate && python3 wiz3.py --ip 192.168.1.109 --action off" --workdir "."
    - Set Color (e.g., RED):
      openclaw exec --command "source venv/bin/activate && python3 wiz3.py --ip 192.168.1.109 --action color --r 255 --g 0 --b 0" --workdir "."

    IMPORTANT: If you encounter "Connection Error" or "Connection refused",
    ensure the bulb is powered on and its IP address is correct (it might change!).

"""

import sys
import subprocess
import importlib.util
import argparse
import asyncio
import time

# Check if pywizlight is installed. If not, exit with an error and instructions.
if importlib.util.find_spec("pywizlight") is None:
    print("❌ Error: 'pywizlight' not found. Please follow the instructions in the script's docstring to set up a virtual environment and install dependencies.")
    sys.exit(1)

from pywizlight import wizlight, PilotBuilder

# 🔥 Workaround for a known pywizlight + Python 3.12 shutdown bug
# Prevents RuntimeError: "Event loop is closed" during interpreter exit
wizlight.__del__ = lambda self: None

async def control_wiz(ip: str, action: str, red: int = 0, green: int = 0, blue: int = 0, duration: int = 0):
    print(f"🔌 Connecting to Wiz Bulb at {ip}...")
    
    try:
        light = wizlight(ip)
        
        if action == "on":
            print("💡 Turning light ON...")
            await light.turn_on(PilotBuilder(brightness=255))
        
        elif action == "off":
            print("🌑 Turning light OFF...")
            await light.turn_off()
        
        elif action == "color":
            print(f"🎨 Setting color to R:{red} G:{green} B:{blue}...")
            await light.turn_on(PilotBuilder(rgb=(red, green, blue), brightness=255))
        
        elif action == "disco":
            print("🕺 Starting disco mode!")
            colors = [
                (255, 0, 0),    # Red
                (0, 255, 0),    # Green
                (0, 0, 255),    # Blue
                (255, 255, 0),  # Yellow
                (0, 255, 255),  # Cyan
                (255, 0, 255)   # Magenta
            ]
            
            start_time = time.time()
            i = 0
            while True:
                if duration > 0 and (time.time() - start_time) > duration:
                    print(f"🎉 Disco mode finished after {duration} seconds.")
                    break
                
                color = colors[i % len(colors)]
                print(f"🎨 Setting color to R:{color[0]} G:{color[1]} B:{color[2]}...")
                await light.turn_on(PilotBuilder(rgb=color, brightness=255))
                await asyncio.sleep(0.5) # Wait 0.5 seconds before changing color
                i += 1

        print("✅ Operation successful!")

    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print("Tip: Ensure the bulb is powered on and the IP is correct.")

def main():
    parser = argparse.ArgumentParser(description="Control Wiz Smart Light via CLI")
    
    parser.add_argument("--ip", type=str, required=True, help="IP address of the bulb")
    parser.add_argument("--action", type=str, choices=["on", "off", "color", "disco"], required=True, help="Action to perform")
    
    # Optional RGB arguments for 'color' action
    parser.add_argument("--r", type=int, default=0, help="Red (0-255)")
    parser.add_argument("--g", type=int, default=0, help="Green (0-255)")
    parser.add_argument("--b", type=int, default=0, help="Blue (0-255)")

    # Optional duration for 'disco' action
    parser.add_argument("--duration", type=int, default=0, help="Duration in seconds for disco mode (0 for infinite)")

    args = parser.parse_args()

    # Run Async Loop
    try:
        asyncio.run(control_wiz(args.ip, args.action, args.r, args.g, args.b, args.duration))
    except KeyboardInterrupt:
        print(" Disco mode interrupted.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
