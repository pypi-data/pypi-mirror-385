"""Configuration UI screen"""

from pathlib import Path
from rich.text import Text
import questionary
from .base_ui import BaseUI

class ConfigurationUI(BaseUI):
    def show(self):
        """Display configuration management screen"""
        self.clear_screen()
        
        # Title
        title_text = Text("Configuration Management", style=self.theme.TextStyles.TITLE)
        title_panel = self.create_centered_panel(title_text, self.theme.Titles.CONFIGURATION)
        self.console.print(title_panel)
        self.console.print()
        
        try:
            # Import here to avoid circular import
            from ..config import get_config, config_manager
            
            # Try to load config using centralized manager
            config = get_config()
            config_path = Path("tng_config.py")
            
            # Show config summary using the manager
            config_manager.display_config_summary()
            self.console.print()
            
            action = questionary.select(
                self.theme.Messages.SELECT_OPTION,
                choices=self.theme.MenuOptions.CONFIG_ACTIONS,
                style=self.get_common_style()
            ).ask()
            
            if action == f"{self.theme.Icons.VIEW}  View current configuration":
                self._show_config_content(config_path)
            elif action == f"{self.theme.Icons.REGENERATE}  Regenerate configuration":
                self._regenerate_config()
                
        except FileNotFoundError:
            # No config found
            warning_text = Text()
            warning_text.append(f"{self.theme.Icons.WARNING} {self.theme.Messages.CONFIG_MISSING}\n", style=self.theme.Colors.WARNING)
            warning_text.append("A configuration file is needed for TNG to work properly.", style=self.theme.Colors.TEXT_PRIMARY)
            
            warning_panel = self.create_centered_panel(warning_text, self.theme.Titles.CONFIGURATION_MISSING)
            self.console.print(warning_panel)
            self.console.print()
            
            if questionary.confirm("Generate configuration file?", style=self.get_common_style()).ask():
                self._regenerate_config()
        except Exception as e:
            error_text = Text(f"Error loading configuration: {str(e)}", style=self.theme.Colors.ERROR)
            error_panel = self.create_centered_panel(error_text, self.theme.Titles.ERROR)
            self.console.print(error_panel)
            self.console.print()
            
            if questionary.confirm("Try to regenerate configuration?", style=self.get_common_style()).ask():
                self._regenerate_config()
    
    def _show_config_content(self, config_path):
        """Show configuration file content"""
        self.clear_screen()
        
        try:
            with open(config_path) as f:
                content = f.read()
            
            # Truncate if too long
            if len(content) > 1000:
                content = content[:1000] + "\n\n... (truncated)"
            
            content_panel = self.create_centered_panel(
                Text(content, style=self.theme.Colors.TEXT_PRIMARY),
                f"{self.theme.Icons.FILE} Configuration File Content"
            )
            self.console.print(content_panel)
            
        except Exception as e:
            error_text = Text(f"Error reading config file: {str(e)}", style=self.theme.Colors.ERROR)
            error_panel = self.create_centered_panel(error_text, f"{self.theme.Icons.ERROR} Error")
            self.console.print(error_panel)
        
        self.press_any_key()
    
    def _regenerate_config(self):
        """Regenerate configuration file"""
        try:
            from ..cli import init_config
            from ..config import config_manager
            init_config()
            
            # Reload config after regeneration
            config_manager.reload_config()
            
            success_text = Text(f" {self.theme.Icons.SUCCESS}  {self.theme.Messages.CONFIG_CREATED}", style=self.theme.format_bold_message("success"))
            success_panel = self.create_centered_panel(success_text, self.theme.Titles.SUCCESS)
            self.console.print(success_panel)
            
        except Exception as e:
            error_text = Text(f" {self.theme.Icons.ERROR} {self.theme.Messages.CONFIG_ERROR.format(error=str(e))}", style=self.theme.format_bold_message("error"))
            error_panel = self.create_centered_panel(error_text, self.theme.Titles.ERROR)
            self.console.print(error_panel)
        
        self.press_any_key()
