"""
GTK4 Tray Icon Module - Easy to integrate StatusNotifierItem + DBusMenu

This module provides a simple API to add a system tray icon with context menu
to any GTK4 application with minimal code changes.

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

Usage:
    from trayer import TrayIcon
    
    # In your GTK4 app:
    tray = TrayIcon(
        app_id="com.example.myapp",
        title="My App",
        icon_name="application-x-executable"
    )
    
    # Add menu items
    tray.add_menu_item("Show", callback=show_window)
    tray.add_menu_item("Quit", callback=quit_app)
    
    # Setup (call before app.run())
    tray.setup()
"""

import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib

# StatusNotifierItem specification
SNI_INTERFACE = "org.kde.StatusNotifierItem"
SNI_PATH = "/StatusNotifierItem"

# DBusMenu specification
DBUSMENU_INTERFACE = "com.canonical.dbusmenu"
DBUSMENU_PATH = "/MenuBar"

# StatusNotifierWatcher
SNW_BUS_NAME = "org.kde.StatusNotifierWatcher"
SNW_OBJECT_PATH = "/StatusNotifierWatcher"
SNW_INTERFACE = "org.kde.StatusNotifierWatcher"


class _DBusMenuService(dbus.service.Object):
    """Internal DBusMenu implementation"""
    
    def __init__(self, bus, menu_items):
        self.bus = bus
        self.menu_items = menu_items  # Reference to TrayIcon.menu_items
        self.revision = 0
        super().__init__(bus, DBUSMENU_PATH)
    
    def _build_menu_structure(self):
        """Build menu structure from menu_items list"""
        structure = {
            0: {'children': []}  # Root
        }
        
        item_id = 1
        for item in self.menu_items:
            if item['type'] == 'separator':
                structure[item_id] = {
                    'type': 'separator',
                    'visible': True
                }
            else:
                structure[item_id] = {
                    'label': item['label'],
                    'enabled': item.get('enabled', True),
                    'visible': item.get('visible', True),
                    'type': 'standard'
                }
            
            structure[0]['children'].append(item_id)
            item['id'] = item_id  # Store ID back to item
            item_id += 1
        
        return structure
    
    def _build_layout(self, parent_id, properties):
        """Build layout for GetLayout"""
        menu = self._build_menu_structure()
        
        if parent_id not in menu:
            return (
                dbus.Int32(parent_id),
                dbus.Dictionary({}, signature='sv'),
                dbus.Array([], signature='(ia{sv}av)')
            )
        
        item = menu[parent_id]
        props = dbus.Dictionary({}, signature='sv')
        
        for key in ['label', 'enabled', 'visible', 'type']:
            if key in item:
                value = item[key]
                if key in ['enabled', 'visible']:
                    props[key] = dbus.Boolean(value)
                else:
                    props[key] = dbus.String(value)
        
        children = dbus.Array([], signature='(ia{sv}av)')
        if 'children' in item:
            for child_id in item['children']:
                child_layout = self._build_layout(child_id, properties)
                child_id_dbus = child_layout[0]
                child_props = child_layout[1] if child_layout[1] else dbus.Dictionary({}, signature='sv')
                child_children = child_layout[2] if child_layout[2] else dbus.Array([], signature='(ia{sv}av)')
                children.append(dbus.Struct((child_id_dbus, child_props, child_children), signature='(ia{sv}av)'))
        
        return (dbus.Int32(parent_id), props, children)
    
    @dbus.service.method(dbus_interface=DBUSMENU_INTERFACE,
                         in_signature='iias', out_signature='u(ia{sv}av)')
    def GetLayout(self, parent_id, recursion_depth, property_names):
        """Get menu layout"""
        layout = self._build_layout(parent_id, property_names)
        return (dbus.UInt32(self.revision), layout)
    
    @dbus.service.method(dbus_interface=DBUSMENU_INTERFACE,
                         in_signature='aias', out_signature='a(ia{sv})')
    def GetGroupProperties(self, ids, property_names):
        """Get properties for multiple items"""
        menu = self._build_menu_structure()
        result = dbus.Array([], signature='(ia{sv})')
        
        for item_id in ids:
            if item_id in menu:
                props = dbus.Dictionary({}, signature='sv')
                item = menu[item_id]
                
                for key in ['label', 'enabled', 'visible', 'type']:
                    if key in item:
                        value = item[key]
                        if key in ['enabled', 'visible']:
                            props[key] = dbus.Boolean(value)
                        else:
                            props[key] = dbus.String(value)
                
                result.append((dbus.Int32(item_id), props))
        
        return result
    
    @dbus.service.method(dbus_interface=DBUSMENU_INTERFACE,
                         in_signature='i', out_signature='b')
    def AboutToShow(self, item_id):
        """Called before showing menu"""
        return dbus.Boolean(False)
    
    @dbus.service.method(dbus_interface=DBUSMENU_INTERFACE,
                         in_signature='isvu', out_signature='')
    def Event(self, item_id, event_type, data, timestamp):
        """Handle menu item clicks"""
        if event_type == 'clicked':
            # Find item by ID and call its callback
            for item in self.menu_items:
                if item.get('id') == item_id and item['type'] != 'separator':
                    callback = item.get('callback')
                    if callback:
                        GLib.idle_add(callback)
                    break
    
    @dbus.service.signal(dbus_interface=DBUSMENU_INTERFACE, signature='a(ia{sv})')
    def ItemsPropertiesUpdated(self, updated_props):
        pass
    
    @dbus.service.signal(dbus_interface=DBUSMENU_INTERFACE, signature='ui')
    def LayoutUpdated(self, revision, parent):
        pass
    
    def update_menu(self):
        """Update menu structure"""
        self.revision += 1
        self.LayoutUpdated(self.revision, 0)


class _StatusNotifierItem(dbus.service.Object):
    """Internal StatusNotifierItem implementation"""
    
    def __init__(self, tray_icon, bus, object_path):
        self.tray = tray_icon
        self.bus = bus
        
        # Generate unique bus name
        self.bus_name_str = f"org.kde.StatusNotifierItem-{tray_icon.app_id}-{id(self)}"
        self.bus_name = dbus.service.BusName(self.bus_name_str, bus)
        
        super().__init__(self.bus_name, object_path)
        
        # Create DBusMenu
        self.menu = _DBusMenuService(bus, tray_icon.menu_items)
        
        # Register with watcher
        self._register_to_watcher()
    
    def _register_to_watcher(self):
        """Register with StatusNotifierWatcher"""
        try:
            watcher = self.bus.get_object(SNW_BUS_NAME, SNW_OBJECT_PATH)
            watcher.RegisterStatusNotifierItem(
                self.bus_name_str,
                dbus_interface=SNW_INTERFACE
            )
        except dbus.exceptions.DBusException:
            pass  # Silent fail, will still work on some DEs
    
    @dbus.service.method(dbus_interface='org.freedesktop.DBus.Properties',
                         in_signature='ss', out_signature='v')
    def Get(self, interface, prop):
        """Get property"""
        try:
            if interface != SNI_INTERFACE:
                # Return an empty DBus string variant instead of None so the
                # dbus library can encode a valid value (None cannot be encoded).
                return dbus.String("")
            
            if prop == 'Status':
                return dbus.String(self.tray.status)
            elif prop == 'Category':
                return dbus.String('ApplicationStatus')
            elif prop == 'Id':
                return dbus.String(self.tray.app_id)
            elif prop == 'Title':
                return dbus.String(self.tray.title)
            elif prop == 'IconName':
                return dbus.String(self.tray.icon_name)
            elif prop == 'Menu':
                return dbus.ObjectPath(DBUSMENU_PATH)
            elif prop == 'ItemIsMenu':
                return dbus.Boolean(True)
            # Unknown property: return empty DBus string variant to avoid
            # "Don't know which D-Bus type to use to encode type NoneType" errors.
            return dbus.String("")
        except Exception as e:
            import sys
            print(f"ERROR in Get({interface}, {prop}): {e}", file=sys.stderr)
            raise
    
    @dbus.service.method(dbus_interface='org.freedesktop.DBus.Properties',
                         in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        """Get all properties"""
        if interface != SNI_INTERFACE:
            return {}
        
        return {
            'Status': dbus.String(self.tray.status),
            'Category': dbus.String('ApplicationStatus'),
            'Id': dbus.String(self.tray.app_id),
            'Title': dbus.String(self.tray.title),
            'IconName': dbus.String(self.tray.icon_name),
            'Menu': dbus.ObjectPath(DBUSMENU_PATH),
            'ItemIsMenu': dbus.Boolean(True),
        }
    
    @dbus.service.method(dbus_interface=SNI_INTERFACE, in_signature='ii', out_signature='')
    def Activate(self, x, y):
        """Left-click"""
        if self.tray.on_left_click:
            GLib.idle_add(self.tray.on_left_click)
    
    @dbus.service.method(dbus_interface=SNI_INTERFACE, in_signature='ii', out_signature='')
    def ContextMenu(self, x, y):
        """Right-click (menu handled by DBusMenu)"""
        pass
    
    @dbus.service.method(dbus_interface=SNI_INTERFACE, in_signature='ii', out_signature='')
    def SecondaryActivate(self, x, y):
        """Middle-click"""
        if self.tray.on_middle_click:
            GLib.idle_add(self.tray.on_middle_click)
    
    @dbus.service.method(dbus_interface=SNI_INTERFACE, in_signature='is', out_signature='')
    def Scroll(self, delta, orientation):
        """Scroll"""
        pass
    
    @dbus.service.signal(dbus_interface=SNI_INTERFACE, signature='s')
    def NewStatus(self, status):
        pass
    
    @dbus.service.signal(dbus_interface=SNI_INTERFACE, signature='')
    def NewIcon(self):
        pass
    
    def change_icon(self, icon_name):
        """Change icon"""
        self.tray.icon_name = icon_name
        self.NewIcon()
    
    def change_status(self, status):
        """Change status"""
        self.tray.status = status
        # Ensure status is a string, not None
        if status is None:
            return
        self.NewStatus(status)


class TrayIcon:
    """
    Easy-to-use tray icon with context menu for GTK4 apps
    
    Example:
        tray = TrayIcon(
            app_id="com.example.myapp",
            title="My Application",
            icon_name="application-x-executable"
        )
        
        tray.set_left_click(lambda: print("Clicked!"))
        tray.add_menu_item("Show", callback=show_window)
        tray.add_menu_separator()
        tray.add_menu_item("Quit", callback=quit_app)
        
        tray.setup()  # Call before app.run()
    """
    
    def __init__(self, app_id, title, icon_name="application-x-executable"):
        """
        Initialize tray icon
        
        Args:
            app_id: Application ID (e.g., "com.example.myapp")
            title: Tray icon tooltip/title
            icon_name: Icon name from theme (e.g., "application-x-executable")
        """
        self.app_id = app_id
        self.title = title
        self.icon_name = icon_name
        self.status = "Active"
        
        self.menu_items = []
        self.on_left_click = None
        self.on_middle_click = None
        
        self._sni = None
        self._bus = None
    
    def set_left_click(self, callback):
        """
        Set callback for left-click on tray icon
        
        Args:
            callback: Function to call (no arguments)
        """
        self.on_left_click = callback
    
    def set_middle_click(self, callback):
        """
        Set callback for middle-click on tray icon
        
        Args:
            callback: Function to call (no arguments)
        """
        self.on_middle_click = callback
    
    def add_menu_item(self, label, callback, enabled=True, visible=True):
        """
        Add a menu item
        
        Args:
            label: Text to display
            callback: Function to call when clicked (no arguments)
            enabled: Whether item is clickable
            visible: Whether item is shown
        """
        self.menu_items.append({
            'type': 'item',
            'label': label,
            'callback': callback,
            'enabled': enabled,
            'visible': visible
        })
    
    def add_menu_separator(self):
        """Add a separator line to the menu"""
        self.menu_items.append({
            'type': 'separator'
        })
    
    def setup(self):
        """
        Setup the tray icon
        
        IMPORTANT: Call this BEFORE app.run() in your GTK4 application!
        
        Example:
            app = MyGtkApp()
            tray = TrayIcon(...)
            tray.setup()
            app.run()
        """
        # Initialize D-Bus
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self._bus = dbus.SessionBus()
        
        # Create StatusNotifierItem
        self._sni = _StatusNotifierItem(self, self._bus, SNI_PATH)
    
    def change_icon(self, icon_name):
        """
        Change the tray icon
        
        Args:
            icon_name: New icon name from theme
        """
        if self._sni:
            self._sni.change_icon(icon_name)
    
    def change_status(self, status):
        """
        Change status (affects visibility/appearance)
        
        Args:
            status: "Active", "Passive", or "NeedsAttention"
        """
        if self._sni and status in ['Active', 'Passive', 'NeedsAttention']:
            self._sni.change_status(status)
    
    def update_menu(self):
        """
        Update menu after adding/removing items dynamically
        
        Call this after modifying menu_items to refresh the menu
        """
        if self._sni:
            self._sni.menu.update_menu()
