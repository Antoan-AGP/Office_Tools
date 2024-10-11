import json
import os
import sys
import requests
from pystray import Icon, MenuItem as Item, Menu
from PIL import Image, ImageDraw
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import threading

# Global variables
config_file = "config.json"
server_url = "http://10.1.0.135:1129/update"
tray_icon = None

# Default configuration
default_config = {
    "name": "User",       # Replace with your default user name
    "feeling": "ok"       # Default feeling is 'ok'
}

def initialize_config():
    # Check if config.json exists
    if not os.path.exists(config_file):
        print(f"{config_file} not found. Creating a new one with default values.")
        save_config(default_config)
    else:
        # If config exists, load and validate it
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Validate that the config has required keys
                if 'name' not in config or 'feeling' not in config:
                    raise ValueError("Invalid config file. Re-creating with default values.")
        except (json.JSONDecodeError, ValueError):
            # If the config is invalid or corrupted, create a new one
            print(f"Error reading {config_file}. Re-creating with default values.")
            save_config(default_config)

def load_config():
    # Load the config file (after initialization ensures it's valid)
    with open(config_file, 'r') as f:
        return json.load(f)

def save_config(config):
    # Write config to file
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

def update_server(name, feeling):
    # Send the updated data to the server
    data = {"name": name, "feeling": feeling}
    try:
        response = requests.post(server_url, json=data)
        if response.status_code == 200:
            print(f"Status updated to {feeling} for {name}")
        else:
            print(f"Failed to update server: {response.status_code}")
    except Exception as e:
        print(f"Error updating server: {e}")

def start_config_watcher():
    event_handler = ConfigChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

class ConfigChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(config_file):
            # Load the updated config and send it to the server
            config = load_config()
            update_server(config['name'], config['feeling'])
            # Update the tray icon and tooltip
            update_tray_icon(config['feeling'])

def update_feeling(feeling):
    config = load_config()
    config["feeling"] = feeling
    save_config(config)

    # Send the update to the server
    update_server(config['name'], feeling)

    # Update tray icon color
    update_tray_icon(feeling)

def update_tray_icon(feeling):
    color_map = {
        "cold": (0, 0, 255),  # Blue for cold
        "ok": (0, 255, 0),    # Green for ok
        "warm": (255, 165, 0)  # Orange for warm
    }
    icon = create_circular_icon(color_map[feeling])
    tray_icon.icon = icon
    tray_icon.title = f"Temperature Status: {feeling.capitalize()}"  # Update tooltip

def create_circular_icon(color):
    # Circle dimensions
    width = 64
    height = 64
    radius = 32

    # Create a new image with a transparent background (RGBA mode)
    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))  # Transparent background
    draw = ImageDraw.Draw(image)

    # Draw a filled circle
    draw.ellipse((0, 0, width, height), fill=color)

    return image

def on_quit(icon, item):
    config = load_config()
    # Send a request to remove the user's response from the server
    url = server_url
    data = {"name": config['name']}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print(f"{config['name']}'s response removed from the server")
        else:
            print(f"Failed to remove response: {response.status_code}")
    except Exception as e:
        print(f"Error removing response: {e}")
    
    icon.stop()

def show_settings(icon, item):
    os.system(f'notepad {config_file}')

def setup_tray_icon():
    global tray_icon
    config = load_config()

    # Create the "Feeling" dropdown with nested options
    feeling_menu = Menu(
        Item("Cold", lambda: update_feeling("cold")),
        Item("Ok", lambda: update_feeling("ok")),
        Item("Warm", lambda: update_feeling("warm"))
    )

    # Main tray menu
    menu = Menu(
        Item("Feeling", feeling_menu),
        Item("Settings", show_settings),
        Item("Quit", on_quit)
    )

    # Set up the tray icon with a tooltip
    tray_icon = Icon(
        "temp_status",
        icon=create_circular_icon((0, 255, 0)),  # Default to green (ok)
        menu=menu,
        title=f"1129 Temperature Status: {config['feeling'].capitalize()}"
    )

    update_tray_icon(config["feeling"])
    tray_icon.run()

if __name__ == "__main__":
    initialize_config()
    setup_tray_icon()
    # Start the config file watcher in a separate thread
    #config_watcher_thread = threading.Thread(target=start_config_watcher, daemon=True)
    #config_watcher_thread.start()
