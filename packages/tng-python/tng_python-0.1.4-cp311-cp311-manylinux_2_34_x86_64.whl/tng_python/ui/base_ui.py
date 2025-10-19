"""Base UI class with common styling and layout"""

from rich.console import Console
from rich.panel import Panel
from rich.align import Align
import questionary
from .theme import TngTheme

class BaseUI:
    def __init__(self):
        self.console = Console()
        self.theme = TngTheme()
        
    def get_common_style(self):
        """Common questionary style for all screens"""
        return self.theme.get_questionary_style()
    
    def create_centered_panel(self, content, title, border_style=None):
        """Create a centered panel with consistent styling"""
        if border_style is None:
            border_style = self.theme.Colors.BORDER_DEFAULT
            
        panel = Panel(
            Align.center(content),
            title=title,
            border_style=border_style,
            padding=self.theme.Layout.PANEL_PADDING,
            box=self.theme.Layout.PANEL_BOX_STYLE
        )
        return panel
    
    def show_banner(self):
        """Display TNG banner"""
        from rich.text import Text
        
        banner = Text()
        banner.append(f"{self.theme.Icons.ROCKET} TNG Python", style=self.theme.TextStyles.TITLE)
        banner.append("\nLLM-Powered Test Generation for Python Applications", style=self.theme.Colors.TEXT_PRIMARY)
        
        panel = self.create_centered_panel(
            banner,
            title=self.theme.Titles.WELCOME,
            border_style=self.theme.Colors.BORDER_DEFAULT
        )
        self.console.print(panel)
        self.console.print()
    
    def clear_screen(self):
        """Clear the screen"""
        self.console.clear()
    
    def press_any_key(self, message=None):
        """Press any key to continue"""
        if message is None:
            message = self.theme.Messages.PRESS_ANY_KEY
        questionary.press_any_key_to_continue(message).ask()
