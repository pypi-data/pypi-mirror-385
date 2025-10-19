"""Project statistics UI screen"""

from rich.table import Table
from .base_ui import BaseUI
from ..http_client import get_http_client

class StatsUI(BaseUI):
    STATS_URL = '/cli/tng_python/stats'
    def show(self):
        """Display API statistics screen"""
        self.clear_screen()
        
        # Get terminal width for proper centering
        terminal_width = self.theme.get_terminal_width()
        
        title_text = f"{self.theme.Icons.STATS} API Usage Statistics"
        centered_title = self.theme.center_text(title_text, terminal_width)
        self.console.print(f"[{self.theme.TextStyles.TITLE}]{centered_title}[/{self.theme.TextStyles.TITLE}]")
        self.console.print()
        
        # Get user API stats
        api_stats = self._get_user_api_stats()
        
        # Display API stats
        if api_stats:
            if api_stats.get("API Status") == "No API key configured":
                self._display_no_api_key_message(terminal_width)
            elif self.theme.Icons.ERROR in api_stats.get("API Status", ""):
                self._display_api_error(api_stats, terminal_width)
            else:
                self._display_api_stats_box(api_stats, terminal_width)
                
                # Display usage progress if we have API data
                if "API Runs Used" in api_stats and "API Runs Limit" in api_stats:
                    self._display_usage_progress(api_stats, terminal_width)
        
        self.console.print()
        tip_msg = f"{self.theme.Icons.LIGHTBULB} Tip: Contact support if you need more test generations"
        centered_tip = self.theme.center_text(tip_msg, terminal_width)
        self.console.print(f"[{self.theme.Colors.TEXT_MUTED}]{centered_tip}[/{self.theme.Colors.TEXT_MUTED}]")
        
        self.press_any_key()
    
    
    def _get_user_api_stats(self):
        """Get user statistics from API using HTTP client"""
        try:
            client = get_http_client()
            
            if not client.api_key:
                return {"API Status": "No API key configured"}
            
            api_data = client._make_request(self.STATS_URL, method='GET')
            
            if api_data:
                stats = {}
                if 'runs' in api_data:
                    stats["API Runs Used"] = api_data['runs']
                if 'max_runs' in api_data:
                    stats["API Runs Limit"] = api_data['max_runs']
                    # Calculate usage percentage
                    if 'runs' in api_data:
                        usage_pct = (api_data['runs'] / api_data['max_runs']) * 100
                        stats["API Usage"] = f"{usage_pct:.1f}%"
                if 'request_id' in api_data:
                    stats["Request ID"] = api_data['request_id'][:10] + "..."  # Show first 8 chars
                
                stats["API Status"] = f"{self.theme.Icons.SUCCESS} Connected"
                return stats
            else:
                return {"API Status": f"{self.theme.Icons.ERROR} Failed to fetch stats"}
            
        except Exception as e:
            return {"API Status": f"{self.theme.Icons.ERROR} Error: {str(e)}"}
    
    def _display_no_api_key_message(self, terminal_width):
        """Display message when no API key is configured"""
        box_width = self.theme.calculate_box_width(terminal_width)
        
        content_lines = [
            f"[{self.theme.TextStyles.WARNING_MESSAGE}]{self.theme.Icons.WARNING} No API Key Configured[/{self.theme.TextStyles.WARNING_MESSAGE}]",
            "",
            f"[{self.theme.TextStyles.BODY}]To view your API usage statistics, you need to configure your API key.[/{self.theme.TextStyles.BODY}]",
            "",
            f"[{self.theme.TextStyles.INSTRUCTION}]Run '{self.theme.Icons.CONFIG} tng init' to set up your configuration.[/{self.theme.TextStyles.INSTRUCTION}]"
        ]
        
        centered_box = self.theme.center_box(content_lines, box_width, terminal_width)
        self.console.print(centered_box)
        self.console.print()
    
    def _display_api_error(self, api_stats, terminal_width):
        """Display API error message"""
        box_width = self.theme.calculate_box_width(terminal_width)
        
        error_msg = api_stats.get("API Status", "Unknown error")
        content_lines = [
            f"[{self.theme.TextStyles.ERROR_MESSAGE}]{self.theme.Icons.ERROR} API Connection Failed[/{self.theme.TextStyles.ERROR_MESSAGE}]",
            "",
            f"[{self.theme.TextStyles.BODY}]{self.theme.Icons.INFO} Status: {str(error_msg)}[/{self.theme.TextStyles.BODY}]",
            "",
            f"[{self.theme.TextStyles.INSTRUCTION}]{self.theme.Icons.LIGHTBULB} Please check your API key and internet connection.[/{self.theme.TextStyles.INSTRUCTION}]"
        ]
        
        centered_box = self.theme.center_box(content_lines, box_width, terminal_width)
        self.console.print(centered_box)
        self.console.print()
    
    
    def _display_api_stats_box(self, stats, terminal_width):
        """Display API statistics using a Rich Table"""
        # Create a beautiful table for the stats
        table = Table(
            title=f"{self.theme.Icons.SUCCESS} Your TNG Account",
            title_style=f"{self.theme.Colors.SUCCESS} bold",
            show_header=False,
            box=self.theme.Layout.PANEL_BOX_STYLE,
            padding=self.theme.Layout.TABLE_PADDING,
            min_width=50
        )
        
        table.add_column("Metric", style=self.theme.TextStyles.BODY_BOLD, no_wrap=True)
        table.add_column("Value", style=self.theme.TextStyles.SUCCESS_MESSAGE)
        
        if "API Runs Used" in stats and "API Runs Limit" in stats:
            used = stats["API Runs Used"]
            limit = stats["API Runs Limit"]
            table.add_row(f"{self.theme.Icons.TEST} Test Generations", f"{used} of {limit} used")
            
            # Calculate remaining
            remaining = limit - used
            if remaining > 0:
                table.add_row(f"{self.theme.Icons.ROCKET} Remaining", f"{remaining} generations")
            else:
                table.add_row(f"{self.theme.Icons.WARNING} Remaining", f"[{self.theme.TextStyles.ERROR_MESSAGE}]0 generations[/{self.theme.TextStyles.ERROR_MESSAGE}]")
        
        if "API Usage" in stats:
            usage = stats["API Usage"]
            table.add_row(f"{self.theme.Icons.CHART} Usage", usage)
        
        if "Request ID" in stats:
            request_id = stats["Request ID"]
            table.add_row(f"{self.theme.Icons.INFO}  Request ID ", f"[{self.theme.TextStyles.DESCRIPTION}]{request_id}[/{self.theme.TextStyles.DESCRIPTION}]")
        
        # Add status
        if "API Status" in stats:
            status = stats["API Status"]
            table.add_row(f"{self.theme.Icons.LINK} Connection", status)
        
        # Center the table
        table_width = 60  # Approximate table width
        left_padding = (terminal_width - table_width) // 2
        if left_padding > 0:
            self.console.print(" " * left_padding, end="")
        
        self.console.print(table)
        self.console.print()
    
    def _display_usage_progress(self, stats, terminal_width):
        runs = int(stats.get("API Runs Used", 0))
        max_runs = int(stats.get("API Runs Limit", 1))
        
        usage_percent = (runs / max_runs * 100) if max_runs > 0 else 0
        
        # Display usage overview title
        usage_title = f"{self.theme.Icons.CHART} Usage Overview"
        centered_usage_title = self.theme.center_text(usage_title, terminal_width)
        self.console.print(f"[{self.theme.TextStyles.SUBTITLE}]{centered_usage_title}[/{self.theme.TextStyles.SUBTITLE}]")
        self.console.print()
        
        # Create progress bar
        from rich.progress import Progress, BarColumn, TextColumn, MofNCompleteColumn
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            MofNCompleteColumn(),
            TextColumn("({task.completed}/{task.total})"),
            console=self.console,
        ) as progress:
            
            # Determine color and message based on usage
            if usage_percent <= 50:
                status_msg = f"{self.theme.Icons.ROCKET} Excellent! Plenty of generations remaining"
            elif usage_percent <= 80:
                status_msg = f"{self.theme.Icons.LIGHTBULB} Good usage - consider monitoring"
            elif usage_percent <= 95:
                status_msg = f"{self.theme.Icons.TIME} High usage - approaching limit"
            else:
                status_msg = f"{self.theme.Icons.SUPPORT} Limit reached - contact support for more runs"
            
            task = progress.add_task(f"{self.theme.Icons.CHART} Usage: ", total=max_runs, completed=runs)
            
            # Animate progress bar
            import time
            current = 0
            step = max(runs // 10, 1)
            while current < runs:
                current = min(current + step, runs)
                progress.update(task, completed=current)
                if runs > 10:
                    time.sleep(0.05)
        
        self.console.print()
        
        # Display status message
        centered_status = self.theme.center_text(status_msg, terminal_width)
        
        if usage_percent <= 50:
            style = self.theme.TextStyles.SUCCESS_MESSAGE
        elif usage_percent <= 80:
            style = self.theme.TextStyles.WARNING_MESSAGE
        else:
            style = self.theme.TextStyles.ERROR_MESSAGE
            
        self.console.print(f"[{style}]{centered_status}[/{style}]")
        self.console.print()
