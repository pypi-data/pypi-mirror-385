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

License: MIT
Author: Matteo Benedetto <me@enne2.net>
Copyright © 2025 Matteo Benedetto

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__version__ = "0.1.1"
__author__ = "Matteo Benedetto"
__email__ = "me@enne2.net"
__license__ = "MIT"
__url__ = "https://github.com/enne2/trayer"

from .tray_icon import TrayIcon

__all__ = ["TrayIcon"]
