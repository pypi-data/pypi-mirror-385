"""
trayer - System Tray Icons for GTK4
====================================

Etymology: From "tray" + "-er" (one who creates trays), and coincidentally
from Middle English "traitor" — because this library gleefully betrays GNOME 3's
philosophy of hiding tray icons. 😈

Add system tray icons to your GTK4 applications with just a few lines!

Basic usage:
    >>> from trayer import TrayIcon
    >>> 
    >>> tray = TrayIcon(
    ...     app_id="com.example.myapp",
    ...     title="My Application",
    ...     icon_name="application-x-executable"
    ... )
    >>> 
    >>> tray.add_menu_item("Show", callback=show_window)
    >>> tray.add_menu_item("Quit", callback=quit_app)
    >>> tray.setup()

For more information, see: https://github.com/enne2/trayer
"""

__version__ = "0.1.0"
__author__ = "enne2"
__license__ = "MIT"

from .tray_icon import TrayIcon

__all__ = ["TrayIcon"]
