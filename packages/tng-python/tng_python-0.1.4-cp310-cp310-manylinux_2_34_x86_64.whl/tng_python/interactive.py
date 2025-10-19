"""Main interactive interface for TNG Python"""

import sys
from enum import Enum
from .ui import BaseUI, StatsUI, AboutUI, HelpUI, GenerateTestsUI, ExitUI, WarningUI, OptionsUI
import questionary

class MenuAction(Enum):
    GENERATE_TESTS = "generate_tests"
    STATS = "stats"
    OPTIONS = "options"
    ABOUT = "about"
    HELP = "help"
    EXIT = "exit"

class TngInteractive(BaseUI):
    def __init__(self):
        super().__init__()
        self.stats_ui = StatsUI()
        self.about_ui = AboutUI()
        self.help_ui = HelpUI()
        self.generate_tests_ui = GenerateTestsUI()
        self.exit_ui = ExitUI()
        self.warning_ui = WarningUI()
        self.options_ui = OptionsUI()
        
    def show_main_menu(self):
        """Display main interactive menu with arrow key navigation"""
        # Check warnings first
        while True:
            warning_result = self.warning_ui.show_warnings()
            if warning_result == "exit":
                self.exit_ui.show()
                sys.exit(0)
            elif warning_result == "continue":
                continue  # Show warnings again
            elif warning_result == False:
                break  # No warnings or user chose to continue
        
        # Main menu loop
        while True:
            self.clear_screen()
            self.show_banner()
            
            choice = questionary.select(
                self.theme.Messages.SELECT_OPTION,
                choices=[
                    questionary.Choice(self.theme.MenuOptions.MAIN_MENU[0], MenuAction.GENERATE_TESTS),
                    questionary.Choice(self.theme.MenuOptions.MAIN_MENU[1], MenuAction.STATS),
                    questionary.Choice(self.theme.MenuOptions.MAIN_MENU[2], MenuAction.OPTIONS),
                    questionary.Choice(self.theme.MenuOptions.MAIN_MENU[3], MenuAction.ABOUT),
                    questionary.Choice(self.theme.MenuOptions.MAIN_MENU[4], MenuAction.HELP),
                    questionary.Choice(self.theme.MenuOptions.MAIN_MENU[6], MenuAction.EXIT)
                ],
                style=self.get_common_style()
            ).ask()
            
            if choice == MenuAction.GENERATE_TESTS:
                self.generate_tests_ui.show()
            elif choice == MenuAction.STATS:
                self.stats_ui.show()
            elif choice == MenuAction.OPTIONS:
                result = self.options_ui.show_main_options_menu()
                if result == "generate_config":
                    from .cli import init_config
                    init_config()
            elif choice == MenuAction.ABOUT:
                self.about_ui.show()
            elif choice == MenuAction.HELP:
                self.help_ui.show()
            elif choice == MenuAction.EXIT or choice is None:
                self.exit_ui.show()
                sys.exit(0)

def main():
    """Main entry point for interactive mode"""
    try:
        app = TngInteractive()
        app.show_main_menu()
    except KeyboardInterrupt:
        try:
            app = TngInteractive()
            app.exit_ui.show()
        except:
            print("\n[yellow]Goodbye! 👋[/yellow]")
        sys.exit(0)
    except Exception as e:
        print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()