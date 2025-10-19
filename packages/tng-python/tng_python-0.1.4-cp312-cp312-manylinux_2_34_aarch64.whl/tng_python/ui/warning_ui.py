"""Warning UI screen for configuration issues"""

from rich.text import Text
import questionary
from enum import Enum
from .base_ui import BaseUI
from ..config import  get_api_key, get_base_url

class WarningAction(Enum):
    FIX_CONFIG = "fix_config"
    EXIT_APP = "exit_app"

class WarningUI(BaseUI):
    def __init__(self):
        super().__init__()
        self.warnings = []
    
    def check_configuration_issues(self):
        """Check for configuration issues and collect warnings"""
        self.warnings = []
        
        # Try to load config using centralized manager
        try:
            # Check API_KEY using centralized function
            api_key = get_api_key()
            if not api_key:
                self.warnings.append({
                    'type': 'error',
                    'title': 'API Key Not Set',
                    'message': 'TNG API_KEY is not configured or empty',
                    'solution': 'Set your API key in tng_config.py: API_KEY = "your-key-here"',
                    'icon': self.theme.Icons.ERROR
                })
                return self.warnings
            
            # Check BASE_URL using centralized function
            base_url = get_base_url()
            if not base_url:
                self.warnings.append({
                    'type': 'error',
                    'title': 'Base URL Not Set',
                    'message': 'TNG BASE_URL is not configured or empty',
                    'solution': 'Set BASE_URL in tng_config.py to your TNG API endpoint',
                    'icon': self.theme.Icons.ERROR
                })
                return self.warnings
            
            # Both API_KEY and BASE_URL are set, now make API call
            from .. import __version__
            from ..http_client import get_http_client
            
            client = get_http_client()
            ping_response = client.ping()
            print(ping_response)
            
            if not ping_response:
                self.warnings.append({
                    'type': 'error',
                    'title': 'API Connection Failed',
                    'message': 'Cannot connect to TNG API - check BASE_URL and internet connection',
                    'solution': 'Verify BASE_URL in tng_config.py and check network connectivity',
                    'icon': self.theme.Icons.ERROR
                })
                return self.warnings
            
            # Check version mismatch
            api_version = ping_response.get('current_version', {}).get('pip_version')
            if api_version and __version__ != api_version:
                self.warnings.append({
                    'type': 'warning',
                    'title': 'Version Mismatch',
                    'message': f'Local version ({__version__}) differs from API version ({api_version})',
                    'solution': f'Update to version {api_version}: pip install tng-python=={api_version}',
                    'icon': self.theme.Icons.WARNING
                })
            
            # Check URL mismatch
            expected_url = ping_response.get('api_info', {}).get('base_url')
            if expected_url and base_url != expected_url.rstrip('/'):
                self.warnings.append({
                    'type': 'warning',
                    'title': 'URL Mismatch',
                    'message': f'Configured URL ({base_url}) differs from expected ({expected_url})',
                    'solution': f'Update BASE_URL in tng_config.py to: {expected_url}',
                    'icon': self.theme.Icons.WARNING
                })
                
        except FileNotFoundError:
            self.warnings.append({
                'type': 'error',
                'title': 'Configuration File Missing',
                'message': 'TNG configuration file (tng_config.py) not found',
                'solution': 'Run "tng-init" to generate configuration file',
                'icon': self.theme.Icons.ERROR
            })
            return self.warnings
        except Exception as e:
            self.warnings.append({
                'type': 'error',
                'title': 'Configuration Load Failed',
                'message': f'Could not load TngConfig: {str(e)}',
                'solution': 'Check tng_config.py syntax or regenerate with "tng-init"',
                'icon': self.theme.Icons.ERROR
            })
            return self.warnings
        
        return self.warnings
    
    
    
    def show_warnings(self):
        """Display warnings screen if there are any issues"""
        warnings = self.check_configuration_issues()
        
        if not warnings:
            return False  # No warnings to show
        
        self.clear_screen()
        
        title_text = Text("Configuration Warnings", style=self.theme.TextStyles.WARNING_MESSAGE)
        title_panel = self.create_centered_panel(title_text, self.theme.Titles.ATTENTION_REQUIRED)
        self.console.print(title_panel)
        self.console.print()
        
        for i, warning in enumerate(warnings, 1):
            self._show_warning_item(warning, i)
            self.console.print()
        
        action = questionary.select(
            self.theme.Messages.SELECT_OPTION,
            choices=[
                questionary.Choice(f"{self.theme.Icons.FIX}  Fix Configuration Issues", WarningAction.FIX_CONFIG),
                questionary.Choice(f"{self.theme.Icons.EXIT}  Exit Application", WarningAction.EXIT_APP),
            ],
            style=self.get_common_style()
        ).ask()
        
        if action == WarningAction.FIX_CONFIG:
            self._show_fix_instructions()
            return "continue"
        elif action == WarningAction.EXIT_APP:
            return "exit"
        
        return "continue"  # Default: show warnings again
    
    def _show_warning_item(self, warning, index):
        """Display a single warning item"""
        warning_text = Text()
        
        style = self.theme.Colors.ERROR if warning['type'] == 'error' else self.theme.Colors.WARNING if warning['type'] == 'warning' else self.theme.Colors.INFO
        warning_text.append(f"{warning['icon']} {warning['title']}\n", style=f"bold {style}")
        
        warning_text.append(f"{warning['message']}\n", style=self.theme.Colors.TEXT_PRIMARY)
        
        warning_text.append(f"{self.theme.Icons.LIGHTBULB}  Solution: {warning['solution']}", style=self.theme.Colors.TEXT_MUTED)
        
        panel_title = f"Issue #{index}"
        border_style = self.theme.Colors.BORDER_ERROR if warning['type'] == 'error' else self.theme.Colors.BORDER_WARNING
        
        warning_panel = self.create_centered_panel(
            warning_text,
            title=panel_title,
            border_style=border_style
        )
        
        self.console.print(warning_panel)
    
    def _show_fix_instructions(self):
        """Show detailed fix instructions"""
        self.clear_screen()
        
        instructions_text = Text()
        instructions_text.append("Configuration Fix Instructions\n\n", style=self.theme.TextStyles.TITLE)
        
        for i, warning in enumerate(self.warnings, 1):
            instructions_text.append(f"{i}. {warning['title']}\n", style=self.theme.TextStyles.HEADER)
            instructions_text.append(f"   {warning['solution']}\n\n", style=self.theme.Colors.TEXT_PRIMARY)
        
        instructions_text.append("After making changes, restart TNG to apply them.", style=self.theme.Colors.TEXT_MUTED)
        
        instructions_panel = self.create_centered_panel(
            instructions_text,
            title=f"{self.theme.Icons.FIX}  How to Fix",
            border_style=self.theme.Colors.BORDER_SUCCESS
        )
        
        self.console.print(instructions_panel)
        self.press_any_key()
    
    
