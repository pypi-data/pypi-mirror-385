"""Help UI screen"""

from rich.text import Text
from rich.table import Table
from .base_ui import BaseUI

class HelpUI(BaseUI):
    def show(self):
        """Display help information screen"""
        self.clear_screen()
        
        # Title
        title_text = Text("TNG Python - LLM-Powered Test Generation", style=self.theme.TextStyles.TITLE)
        title_panel = self.create_centered_panel(title_text, self.theme.Titles.HELP)
        self.console.print(title_panel)
        self.console.print()
        
        # Commands table
        help_table = Table(
            title="Available Commands", 
            show_header=True, 
            header_style=self.theme.TextStyles.HEADER,
            box=self.theme.Layout.PANEL_BOX_STYLE
        )
        help_table.add_column("Command", style=self.theme.Colors.PRIMARY, width=self.theme.Layout.TABLE_COLUMN_WIDTH_MEDIUM)
        help_table.add_column("Description", style=self.theme.Colors.TEXT_PRIMARY, width=self.theme.Layout.TABLE_COLUMN_WIDTH_LARGE)
        
        help_table.add_row("tng", "Start interactive test generation mode")
        help_table.add_row("tng -f users.py -m save", "Generate test for specific method")
        help_table.add_row("tng-init", "Generate TNG configuration file")
        help_table.add_row("tng --help", "Show command help")
        
        # Navigation help
        nav_table = Table(
            title="Navigation", 
            show_header=True, 
            header_style=self.theme.TextStyles.HEADER,
            box=self.theme.Layout.PANEL_BOX_STYLE
        )
        nav_table.add_column("Key", style=self.theme.Colors.ACCENT, width=self.theme.Layout.TABLE_COLUMN_WIDTH_SMALL)
        nav_table.add_column("Action", style=self.theme.Colors.TEXT_PRIMARY, width=self.theme.Layout.TABLE_COLUMN_WIDTH_MEDIUM)
        
        nav_table.add_row(f"{self.theme.Icons.ARROW_UP} {self.theme.Icons.ARROW_DOWN}", "Navigate menu options")
        nav_table.add_row("Enter", "Select option")
        nav_table.add_row("Space", "Check/uncheck (multi-select)")
        nav_table.add_row("Ctrl+C", "Exit application")
        
        # Usage tips
        tips_text = Text()
        tips_text.append(f"{self.theme.Icons.LIGHTBULB} How TNG Python Works:\n", style=self.theme.TextStyles.HIGHLIGHT_BOLD)
        tips_text.append(f"{self.theme.Icons.BULLET} Analyzes your Python code structure and dependencies\n", style=self.theme.Colors.TEXT_PRIMARY)
        tips_text.append(f"{self.theme.Icons.BULLET} Detects frameworks (Django, Flask, FastAPI, etc.) automatically\n", style=self.theme.Colors.TEXT_PRIMARY)
        tips_text.append(f"{self.theme.Icons.BULLET} Generates contextual tests that match your project patterns\n", style=self.theme.Colors.TEXT_PRIMARY)
        tips_text.append(f"{self.theme.Icons.BULLET} Supports 50+ Python libraries and frameworks\n", style=self.theme.Colors.TEXT_PRIMARY)
        tips_text.append(f"{self.theme.Icons.BULLET} Method-specific test generation for precise coverage\n", style=self.theme.Colors.TEXT_PRIMARY)
        
        # Create panels
        commands_panel = self.create_centered_panel(help_table, f"{self.theme.Icons.FILE} Commands")
        nav_panel = self.create_centered_panel(nav_table, f"{self.theme.Icons.ARROW_RIGHT} Navigation")
        tips_panel = self.create_centered_panel(tips_text, f"{self.theme.Icons.LIGHTBULB} Usage Tips")
        
        self.console.print(commands_panel)
        self.console.print()
        self.console.print(nav_panel)
        self.console.print()
        self.console.print(tips_panel)
        
        self.press_any_key()
