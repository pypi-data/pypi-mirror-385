from . import dialog, lang, widget, win

# Export messagebox and simpledialog for backward compatibility
from .dialog import messagebox, pathchooser, simpledialog
from .dialog.datepicker import DateEntry, DateFrame

# Export Calendar and DateEntry for backward compatibility
from .widget.calendar import Calendar

# Export Windows-specific flat button as Button
from .win.button import FlatButton as Button

# Export DPI functions for easy access
from .win.dpi import enable_dpi_geometry as dpi

__version__ = "0.1.4"
__all__ = [
    "lang",
    "win",
    "widget",
    "dialog",
    "Button",
    "dpi",
    "Calendar",
    "DateFrame",
    "DateEntry",
    "messagebox",
    "simpledialog",
    "pathchooser",
]
