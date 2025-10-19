"""Exit UI screen"""

from rich.text import Text
import time
from .base_ui import BaseUI

class ExitUI(BaseUI):
    def show(self):
        """Display exit screen with thank you message"""
        self.clear_screen()
        
        thank_you_text = Text()
        thank_you_text.append(f"Thank you for using TNG Python! {self.theme.Icons.ROCKET}\n\n", style=self.theme.TextStyles.TITLE)
        thank_you_text.append("We hope TNG helped generate comprehensive tests for your Python applications.\n\n", style=self.theme.Colors.TEXT_PRIMARY)
        
        tips_text = Text()
        tips_text.append(f"{self.theme.Icons.LIGHTBULB} Remember:\n", style=self.theme.TextStyles.HIGHLIGHT_BOLD)
        tips_text.append(f"{self.theme.Icons.BULLET} Run 'tng-init' to regenerate config for new frameworks\n", style=self.theme.Colors.TEXT_PRIMARY)
        tips_text.append(f"{self.theme.Icons.BULLET} Your Python project configuration is saved in tng_config.py\n", style=self.theme.Colors.TEXT_PRIMARY)
        tips_text.append(f"{self.theme.Icons.BULLET} TNG supports 50+ Python libraries and frameworks\n", style=self.theme.Colors.TEXT_PRIMARY)
        tips_text.append(f"{self.theme.Icons.BULLET} Visit https://tng.sh for updates and documentation\n\n", style=self.theme.Colors.TEXT_PRIMARY)
        
        contact_text = Text()
        contact_text.append(f"{self.theme.Icons.EMAIL} Questions? Contact us at support@tng.sh\n", style=self.theme.Colors.TEXT_MUTED)
        contact_text.append(f"{self.theme.Icons.BUG} Found a bug? We'd love to hear about it.", style=self.theme.Colors.TEXT_MUTED)
        
        exit_content = Text()
        exit_content.append_text(thank_you_text)
        exit_content.append_text(tips_text)
        exit_content.append_text(contact_text)
        
        exit_panel = self.create_centered_panel(
            exit_content,
            title=self.theme.Titles.GOODBYE,
            border_style=self.theme.Colors.BORDER_DEFAULT
        )
        
        self.console.print(exit_panel)
        
        time.sleep(0.4)
        
        self.console.print(f"\n[{self.theme.Colors.SUCCESS}] Happy Python testing! {self.theme.Icons.COMPLETE}[/{self.theme.Colors.SUCCESS}]")
        time.sleep(0.2)
