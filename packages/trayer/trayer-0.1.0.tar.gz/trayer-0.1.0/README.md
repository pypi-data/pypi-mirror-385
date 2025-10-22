# 🗂️ trayer - System Tray Icons for GTK4

[![PyPI version](https://badge.fury.io/py/trayer.svg)](https://pypi.org/project/trayer/)
[![Python Versions](https://img.shields.io/pypi/pyversions/trayer.svg)](https://pypi.org/project/trayer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Etymology:** From "tray" + "-er" (one who creates trays), and coincidentally from Middle English "traitor" — because this library gleefully betrays GNOME 3's philosophy of hiding tray icons. 😈

Add system tray icons with context menus to your GTK4 applications with just a few lines of code!

---

## ✨ Features

- 🎯 **Simple API** - Add tray icons in 3 lines of code
- 🖱️ **Full Click Support** - Left, right, and middle-click actions
- 📋 **Context Menus** - Easy menu creation with separators
- 🔄 **Dynamic Updates** - Change icons and menus at runtime
- 🎨 **Theme Integration** - Uses system icon themes
- 🐧 **Linux Desktop Support** - Works on GNOME (with extension), KDE, XFCE, Cinnamon
- 📦 **Zero Config** - Implements StatusNotifierItem + DBusMenu protocols

---

## 🚀 Quick Start

### Installation

```bash
pip install trayer
```

**System Requirements:**
```bash
# On Debian/Ubuntu:
sudo apt install python3-gi gir1.2-gtk-4.0 python3-dbus

# On GNOME, you also need:
sudo apt install gnome-shell-extension-appindicator
gnome-extensions enable appindicatorsupport@ubuntu.com
# Then logout/login
```

### Basic Usage

```python
from trayer import TrayIcon
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

class MyApp(Gtk.Application):
    def do_activate(self):
        self.window = Gtk.ApplicationWindow(application=self)
        self.window.set_title("My App")
        self.window.present()
    
    def toggle_window(self):
        if self.window.is_visible():
            self.window.hide()
        else:
            self.window.present()

# Create app
app = MyApp(application_id="com.example.myapp")

# Create tray icon
tray = TrayIcon(
    app_id="com.example.myapp",
    title="My Application",
    icon_name="application-x-executable"
)

# Add click action
tray.set_left_click(app.toggle_window)

# Add menu items
tray.add_menu_item("Show Window", callback=lambda: app.window.present())
tray.add_menu_item("Hide Window", callback=lambda: app.window.hide())
tray.add_menu_separator()
tray.add_menu_item("Quit", callback=app.quit)

# Setup and run (IMPORTANT: setup() before run()!)
tray.setup()
app.run()
```

That's it! 🎉

---

## 📖 Documentation

### Create Tray Icon

```python
from trayer import TrayIcon

tray = TrayIcon(
    app_id="com.example.myapp",      # Your application ID
    title="My Application",           # Tooltip text
    icon_name="application-x-executable"  # Icon from theme
)
```

### Click Actions

```python
# Left-click
tray.set_left_click(lambda: print("Left clicked!"))

# Middle-click
tray.set_middle_click(lambda: print("Middle clicked!"))

# Right-click automatically shows the menu
```

### Menu Items

```python
# Add menu item
tray.add_menu_item("Show", callback=show_window)

# Add disabled item
tray.add_menu_item("Premium Feature", callback=None, enabled=False)

# Add separator
tray.add_menu_separator()

# Add quit button
tray.add_menu_item("Quit", callback=app.quit)
```

### Dynamic Updates

```python
# Change icon
tray.change_icon("mail-unread")

# Change status
tray.change_status("NeedsAttention")  # Active, Passive, or NeedsAttention

# Update menu dynamically
tray.menu_items.clear()
tray.add_menu_item("New Item", callback=some_function)
tray.update_menu()
```

### Complete Example

See [`examples/`](examples/) directory for full working examples:
- `example_minimal.py` - Minimal integration
- `example_hide_to_tray.py` - Hide window to tray
- `example_dynamic_icon.py` - Dynamic icon changes
- `example_dynamic_menu.py` - Dynamic menu updates

---

## 🎨 Icon Names

Common icon names from system themes:

**Applications:**
- `application-x-executable`
- `applications-internet`
- `applications-multimedia`

**Status:**
- `user-available` (green)
- `user-busy` (red)
- `user-away` (yellow)

**Mail:**
- `mail-unread`
- `mail-read`

**Symbols:**
- `face-smile`
- `emblem-important`
- `dialog-information`

Find more: Look in `/usr/share/icons/` or use `gtk4-icon-browser`

---

## 🔧 API Reference

### `TrayIcon(app_id, title, icon_name="application-x-executable")`

Create a new tray icon.

**Parameters:**
- `app_id` (str): Application ID
- `title` (str): Tooltip text
- `icon_name` (str): Icon name from system theme

### `tray.set_left_click(callback)`

Set action for left-clicking the tray icon.

### `tray.set_middle_click(callback)`

Set action for middle-clicking the tray icon.

### `tray.add_menu_item(label, callback, enabled=True, visible=True)`

Add a menu item.

### `tray.add_menu_separator()`

Add a separator line to the menu.

### `tray.setup()`

Initialize the tray icon. **Must be called before `app.run()`!**

### `tray.change_icon(icon_name)`

Change the tray icon dynamically.

### `tray.change_status(status)`

Change status: "Active", "Passive", or "NeedsAttention".

### `tray.update_menu()`

Update the menu after modifying items dynamically.

---

## 🐛 Troubleshooting

### Tray icon doesn't appear on GNOME

Install and enable the AppIndicator extension:

```bash
sudo apt install gnome-shell-extension-appindicator
gnome-extensions enable appindicatorsupport@ubuntu.com
# Then logout/login
```

### Menu doesn't show

Make sure you called `tray.setup()` **before** `app.run()`

### Callbacks don't work

Ensure callbacks don't take arguments or use lambda:

```python
# ✅ Correct
tray.add_menu_item("Show", lambda: app.show_window(True))

# ❌ Wrong
tray.add_menu_item("Show", app.show_window(True))
```

---

## 🤝 How It Works

This library implements two D-Bus protocols:

1. **StatusNotifierItem** - The tray icon itself
   - Spec: https://www.freedesktop.org/wiki/Specifications/StatusNotifierItem/

2. **DBusMenu** - The context menu
   - Spec: https://github.com/AyatanaIndicators/libdbusmenu

Your application communicates with the desktop environment via D-Bus to display the icon and menu.

---

## 📋 Requirements

- Python 3.8+
- PyGObject (GTK4 bindings)
- dbus-python
- A desktop environment with StatusNotifierItem support (GNOME with extension, KDE, XFCE, Cinnamon)

---

## 🤔 Why "trayer"?

The name has a double meaning:

1. **"Tray-er"** - One who creates trays (like "player", "baker")
2. **"Traitor"** (Middle English) - Because we gleefully betray GNOME 3's philosophy of removing tray icons!

The GNOME team decided tray icons were "legacy" and removed native support. This library brings them back through the StatusNotifierItem protocol. We're the rebels of the desktop world! 😎

---

## 📄 License

MIT License - Use freely in your projects!

---

## 🙏 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 💬 Support

- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/enne2/trayer/issues)
- 📚 **Documentation:** [GitHub Wiki](https://github.com/enne2/trayer/wiki)
- 💡 **Feature Requests:** [GitHub Discussions](https://github.com/enne2/trayer/discussions)

---

**Happy betraying!** 😈🗂️
