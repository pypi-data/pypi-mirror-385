from pathlib import Path
from rich.text import Text
from rich.table import Table
import questionary
import time
from .base_ui import BaseUI
from ..service import GenerateTestService

try:
    from iterfzf import iterfzf
    HAS_FZF = True
except ImportError:
    HAS_FZF = False

class GenerateTestsUI(BaseUI):
    def __init__(self):
        super().__init__()
        self.test_service = GenerateTestService()
    
    def show(self):
        """Main test generation flow"""
        while True:
            result = self._show_file_selection()
            if result == "back":
                return "back"
            elif result == "exit":
                return "exit"

    def _show_file_selection(self):
        """Show file selection interface"""
        self.clear_screen()
        self.show_banner()
        
        # Get user Python files
        python_files = self._get_user_python_files()
        
        if not python_files:
            error_text = Text(self.theme.Messages.NO_FILES_FOUND, style=self.theme.format_bold_message("error"))
            error_panel = self.create_centered_panel(error_text, self.theme.Titles.NO_FILES_FOUND)
            self.console.print(error_panel)
            self.press_any_key()
            return "back"
        
        if HAS_FZF:
            # Show instruction panel before fzf
            instruction_text = Text()
            instruction_text.append(f"{self.theme.Icons.SEARCH} Fuzzy File Search\n\n", style=self.theme.TextStyles.TITLE)
            instruction_text.append(f"{self.theme.Icons.BULLET} Type to filter files\n", style=self.theme.Colors.TEXT_PRIMARY)
            instruction_text.append(f"{self.theme.Icons.BULLET} Use arrow keys to navigate\n", style=self.theme.Colors.TEXT_PRIMARY)
            instruction_text.append(f"{self.theme.Icons.BULLET} Press Enter to select\n", style=self.theme.Colors.TEXT_PRIMARY)
            instruction_text.append(f"{self.theme.Icons.BULLET} Press Ctrl+C to cancel", style=self.theme.Colors.TEXT_PRIMARY)
            
            instruction_panel = self.create_centered_panel(instruction_text, self.theme.Titles.FILE_SELECTION)
            self.console.print(instruction_panel)
            self.console.print()
            
            # Use fzf for fuzzy search
            file_options = [f"{file.name} ({file.parent})" for file in python_files]
            file_options.append(self.theme.format_back_option())
            
            selected = iterfzf(
                file_options,
                prompt=f"Select file ({self.theme.Messages.TYPE_TO_FILTER}): "
            )
            
            if not selected or selected == self.theme.format_back_option():
                return "back"
            
            for file in python_files:
                if f"{file.name} ({file.parent})" == selected:
                    selected_file = str(file)
                    break
            else:
                return "back"
        else:
            file_choices = [
                questionary.Choice(self.theme.format_file_display(file.name, file.parent), str(file))
                for file in python_files
            ]
            file_choices.append(questionary.Choice(self.theme.format_back_option(), "back"))
            
            selected_file = questionary.select(
                self.theme.Messages.SELECT_OPTION,
                choices=file_choices,
                style=self.get_common_style()
            ).ask()
            
            if selected_file == "back" or not selected_file:
                return "back"
        
        selected_file_path = Path(selected_file)
        success_text = Text(
            self.theme.format_status_message(
                self.theme.Icons.SUCCESS, 
                self.theme.Messages.FILE_SELECTED.format(filename=selected_file_path.name)
            ), 
            style=self.theme.Colors.SUCCESS
        )
        success_panel = self.create_centered_panel(success_text, self.theme.Titles.FILE_SELECTED)
        self.console.print(success_panel)
        self.console.print()
        
        return self._show_methods_for_file(selected_file)

    def _show_methods_for_file(self, file_path):
        """Show methods for a specific file"""
        self.clear_screen()
        self.show_banner()
        
        methods = self._get_file_methods(file_path)
        
        if not methods:
            error_text = Text(
                self.theme.Messages.NO_METHODS_FOUND.format(filename=Path(file_path).name), 
                style=self.theme.format_bold_message("warning")
            )
            error_panel = self.create_centered_panel(error_text, self.theme.Titles.NO_METHODS_FOUND)
            self.console.print(error_panel)
            self.press_any_key()
            return self._show_file_selection()
        
        file_name = Path(file_path).name
        context_text = Text(
            f"{self.theme.Icons.FOLDER} File: {file_name}\n{self.theme.Icons.METHOD} Found {len(methods)} methods", 
            style=self.theme.Colors.INFO
        )
        
        context_panel = self.create_centered_panel(context_text, self.theme.Titles.METHOD_SELECTION)
        self.console.print(context_panel)
        self.console.print()
        
        if HAS_FZF:
            method_instruction_text = Text()
            method_instruction_text.append(f"{self.theme.Icons.SEARCH} Fuzzy Method Search\n\n", style=self.theme.TextStyles.TITLE)
            method_instruction_text.append(f"{self.theme.Icons.BULLET} Type to filter methods\n", style=self.theme.Colors.TEXT_PRIMARY)
            method_instruction_text.append(f"{self.theme.Icons.BULLET} Use arrow keys to navigate\n", style=self.theme.Colors.TEXT_PRIMARY)
            method_instruction_text.append(f"{self.theme.Icons.BULLET} Press Enter to select method\n", style=self.theme.Colors.TEXT_PRIMARY)
            method_instruction_text.append(f"{self.theme.Icons.BULLET} Press Ctrl+C to cancel", style=self.theme.Colors.TEXT_PRIMARY)
            
            method_instruction_panel = self.create_centered_panel(method_instruction_text, self.theme.Titles.METHOD_SELECTION)
            self.console.print(method_instruction_panel)
            self.console.print()
            
            method_options = methods
            method_options.append(self.theme.format_back_option("File List"))
            
            selected = iterfzf(
                method_options,
                prompt=f"Select method ({self.theme.Messages.TYPE_TO_FILTER}): "
            )
            
            if not selected or selected == self.theme.format_back_option("File List"):
                return self._show_file_selection()
            
            selected_method = selected if selected != self.theme.format_back_option("File List") else None
        else:
            method_choices = [
                questionary.Choice(method, method)
                for method in methods
            ]
            method_choices.append(questionary.Choice(self.theme.format_back_option("File List"), "back"))
            
            selected = questionary.select(
                "Select method to generate test for:",
                choices=method_choices,
                style=self.get_common_style()
            ).ask()
            
            if not selected or selected == "back":
                return self._show_file_selection()
            
            selected_method = selected if selected != "back" else None
        
        if selected_method:
            self.clear_screen()
            self.show_banner()
            
            self._show_selection_summary(file_path, selected_method)
            self._generate_tests_for_method(file_path, selected_method)
            return "back"
        else:
            return self._show_file_selection()

    def _show_selection_summary(self, file_path, selected_method):
        """Show what was selected before generating tests"""
        file_name = Path(file_path).name
        
        table = Table(
            title=f"{self.theme.Icons.STATS} Test Generation Summary", 
            show_header=True, 
            header_style=self.theme.TextStyles.HEADER,
            box=self.theme.Layout.PANEL_BOX_STYLE
        )
        table.add_column("File", style=self.theme.Colors.SUCCESS)
        table.add_column("Selected Method", style=self.theme.Colors.ACCENT)
        
        table.add_row(file_name, selected_method)
        
        summary_panel = self.create_centered_panel(table, self.theme.Titles.READY_TO_GENERATE)
        self.console.print(summary_panel)
        self.console.print()

    def _generate_tests_for_method(self, file_path, selected_method):
        """Generate tests for selected method with enhanced progress UI"""
        # Show initial status
        self.console.print()
        start_text = Text(
            self.theme.format_status_message(self.theme.Icons.ROCKET, self.theme.Messages.GENERATION_START), 
            style=self.theme.format_bold_message("info")
        )
        start_panel = self.create_centered_panel(start_text, self.theme.Titles.TEST_GENERATION)
        self.console.print(start_panel)
        self.console.print()

        start_time = time.time()
        result = self._run_generation_with_progress(selected_method, file_path)
        elapsed = time.time() - start_time

        # Handle error with retry option
        if not result.get('success'):
            error_message = result.get('error', 'Unknown error')
            
            # Show clear error message
            error_text = Text()
            error_text.append("❌ ", style="bright_red")
            error_text.append("Test Generation Failed\n\n", style="bold bright_red")
            error_text.append("Error: ", style="bright_red")
            error_text.append(f"{error_message}\n\n", style="white")
            error_text.append("💡 ", style="bright_yellow")
            error_text.append("This usually happens due to:\n", style="bright_yellow")
            error_text.append("  • Network connectivity issues\n", style="dim white")
            error_text.append("  • API service temporarily unavailable\n", style="dim white")
            
            error_panel = self.create_centered_panel(error_text, "🚨 Generation Error")
            self.console.print(error_panel)
            self.console.print()
            
            # Ask user if they want to retry
            retry_choice = questionary.select(
                "What would you like to do?",
                choices=[
                    questionary.Choice("🔄 Retry generation", "retry"),
                    questionary.Choice("🔙 Go back to method selection", "back"),
                    questionary.Choice("🏠 Return to main menu", "main"),
                ],
                style=self.get_common_style()
            ).ask()
            
            if retry_choice == "retry":
                # Retry the same method
                self.console.print()
                retry_text = Text(
                    "🔄 Retrying test generation...", 
                    style="bright_yellow"
                )
                retry_panel = self.create_centered_panel(retry_text, "Retry Attempt")
                self.console.print(retry_panel)
                self.console.print()
                
                # Recursive call to retry
                return self._generate_tests_for_method(file_path, selected_method)
            elif retry_choice == "back":
                return self._show_methods_for_file(file_path)
            else:
                return "back"

        # Save the generated test file
        self.console.print()
        save_text = Text(
            self.theme.format_status_message(self.theme.Icons.WRITE, "Saving test file..."), 
            style=self.theme.format_bold_message("info")
        )
        save_panel = self.create_centered_panel(save_text, "💾 Saving Test")
        self.console.print(save_panel)
        
        # Save the file using the service
        file_info = self.test_service.save_test_file(result['result'])
        
        if file_info:
            # Success panel
            self.console.print()
            success_text = Text(
                self.theme.format_status_message(self.theme.Icons.COMPLETE, self.theme.Messages.GENERATION_COMPLETE), 
                style=self.theme.format_bold_message("success")
            )
            success_panel = self.create_centered_panel(success_text, self.theme.Titles.GENERATION_COMPLETE)
            self.console.print(success_panel)
            self.console.print()
            
            # Show file details
            stats_table = Table(
                show_header=False, 
                box=self.theme.Layout.PANEL_BOX_STYLE, 
                padding=self.theme.Layout.TABLE_PADDING
            )
            stats_table.add_column(style=self.theme.Colors.INFO)
            stats_table.add_column(style=self.theme.Colors.SUCCESS)
            
            # Count the number of test cases generated (including parametrized tests)
            # Small delay to ensure file is fully written
            time.sleep(0.1)
            test_count = self._count_test_methods(file_info['absolute_path'])
            
            stats_table.add_row(f"{self.theme.Icons.FOLDER} Source File:", Path(file_path).name)
            stats_table.add_row(f"{self.theme.Icons.FILE} Test File:", Path(file_info['file_path']).name)
            # Ensure elapsed time is available (handle recursive calls)
            try:
                stats_table.add_row(f"{self.theme.Icons.TIME} Time Taken: ", f"{elapsed:.1f}s")
            except NameError:
                # elapsed not defined due to recursive call, calculate from start_time if available
                try:
                    current_elapsed = time.time() - start_time
                    stats_table.add_row(f"{self.theme.Icons.TIME} Time Taken: ", f"{current_elapsed:.1f}s")
                except NameError:
                    # start_time also not available, skip time display
                    pass
            if file_info.get('test_class_name'):
                stats_table.add_row(f"{self.theme.Icons.TEST} Test Class:", file_info['test_class_name'])
            stats_table.add_row("🧪 Tests Generated:", f"{test_count} test case{'s' if test_count != 1 else ''}")
            
            stats_panel = self.create_centered_panel(stats_table, self.theme.Titles.GENERATION_STATS)
            self.console.print(stats_panel)
            
            # Show run command and menu
            return self._show_run_command_menu(file_info['file_path'])
        else:
            # File save failed
            error_text = Text(
                self.theme.format_status_message(
                    self.theme.Icons.ERROR, "Failed to save test file"
                ),
                style=self.theme.format_bold_message("error")
            )
            error_panel = self.create_centered_panel(error_text, "❌ Save Failed")
            self.console.print(error_panel)
            self.press_any_key()
            return "back"

    def _get_user_python_files(self):
        """Get Python files that belong to the user's project (not dependencies)"""
        current_dir = Path.cwd()
        python_files = []
        
        exclude_dirs = {
            'venv', 'env', '.venv', '.env',
            'site-packages', 'dist-packages',
            '__pycache__', '.git', '.pytest_cache',
            'node_modules', 'target', 'build', 'dist',
            '.mypy_cache', '.tox', 'htmlcov',
            'tests', 'test', 'spec'
        }
        
        for py_file in current_dir.rglob("*.py"):
            if any(excluded in py_file.parts for excluded in exclude_dirs):
                continue
            
            if py_file.stat().st_size < 10:
                continue
            
            python_files.append(py_file)
        
        # Sort by name for consistent ordering
        return sorted(python_files, key=lambda x: x.name)

    def _get_file_methods(self, file_path):
        """Get method names from Python file using Rust"""
        try:
            import tng_python
            return tng_python.get_method_names(file_path)
            
        except Exception as e:
            self.console.print(f"[red]Error analyzing file: {str(e)}[/red]")
            return []

    def _run_generation_with_progress(self, selected_method, file_path):
        """Run test generation with beautiful animated progress UI"""
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
        from rich.panel import Panel
        from rich.align import Align
        from rich.text import Text
        
        # Enhanced progress stages with beautiful descriptions
        stages = {
            "initializing": {
                "desc": "🎯 Initializing generation engine", 
                "progress": 8,
                "color": "bright_blue",
                "icon": "🎯"
            },
            "analyzing": {
                "desc": "🔬 Deep-scanning source code", 
                "progress": 18,
                "color": "bright_magenta", 
                "icon": "🔬"
            },
            "pending": {
                "desc": "🚀 Launching AI processing", 
                "progress": 30,
                "color": "bright_yellow",
                "icon": "🚀"
            },
            "processing": {
                "desc": "🧠 AI crafting intelligent tests", 
                "progress": 75,
                "color": "bright_cyan",
                "icon": "🧠"
            },
            "finalizing": {
                "desc": "✨ Polishing test structure", 
                "progress": 92,
                "color": "bright_green",
                "icon": "✨"
            },
            "completed": {
                "desc": "🎉 Generation  complete!", 
                "progress": 100,
                "color": "green",
                "icon": "🎉"
            },
            # Additional status handling
            "queued": {
                "desc": "📋 Request queued for processing", 
                "progress": 15,
                "color": "bright_blue",
                "icon": "📋"
            },
            "validating": {
                "desc": "🔍 Validating request parameters", 
                "progress": 12,
                "color": "bright_magenta",
                "icon": "🔍"
            },
            "retrying": {
                "desc": "🔄 Retrying after temporary issue", 
                "progress": 35,
                "color": "bright_yellow",
                "icon": "🔄"
            }
        }
        
        # Track polling for realistic progress
        poll_count = 0
        max_polls = 96  # 480 seconds ÷ 5 seconds = 96 polls max (8 minutes)
        
        # 100+ funny Python facts to show during polling (shuffled each run)
        python_facts = [
            "Python was named after Monty Python's Flying Circus! 🐍",
            "The Zen of Python says 'Simple is better than complex'... then you discover decorators 🤔",
            "Python's creator Guido van Rossum is called the 'Benevolent Dictator for Life' 👑",
            "Python: 'Batteries included!' Also Python: pip install everything 🔋",
            "The Python Package Index (PyPI) has over 400,000 packages! Most do the same thing 📦",
            "Python's 'import this' reveals the Zen of Python easter egg 🥚",
            "Python: 'There should be one obvious way to do it.' *Lists 5 ways* 🤷‍♂️",
            "List comprehensions: Making one-liners that need 10 minutes to understand! ⚡",
            "Python's 'else' clause works with loops. Because why not confuse everyone? 🔄",
            "The walrus operator ':=' - because Python needed more ways to assign variables 🦭",
            "Python's GIL: 'We support multithreading!' *Doesn't actually multithread* 🔒",
            "F-strings are faster than .format()! Only took Python 26 years to figure out 🏃‍♂️",
            "Python has a built-in web server that nobody uses in production 🌐",
            "The 'is' operator: For when '==' is too mainstream 🆔",
            "Python's 'pass' statement: The programming equivalent of 'umm...' 🚫",
            "You can chain comparisons in Python! Math teachers everywhere are confused ⛓️",
            "Python's 'antigravity' module: More useful than most enterprise code 🚀",
            "Dictionaries are ordered in Python 3.7+! Only took 27 years 📚",
            "Python's 'collections.Counter': For when you can't count manually 🔢",
            "The 'itertools' module: Functional programming for people who hate loops ⚒️",
            "Python supports operator overloading: Because + wasn't confusing enough ✨",
            "Lambda functions: Anonymous functions that everyone names anyway 👻",
            "Python's 'with' statement: Finally, automatic cleanup! Only took 15 years 🧹",
            "You can use 'else' with try-except: Because exceptions need happy endings too 🎯",
            "Python's 'yield' creates generators: Lazy evaluation for lazy programmers 🏭",
            "The 'pathlib' module: Object-oriented file paths, because strings were too simple 📁",
            "Python's 'dataclasses': Auto-generating code so you don't have to think 🤖",
            "Type hints don't affect runtime: Annotations that do nothing! Revolutionary! 🐛",
            "Python's 'asyncio': Concurrent programming that's still single-threaded 🔀",
            "The 'functools.lru_cache': Memoization for people who forget things 💾",
            "Python's 'enumerate': For when counting is too hard 📊",
            "The 'zip' function: Pairs things together, unlike Python 2 and 3 🤐",
            "Python's 'any()' and 'all()': Boolean logic for the indecisive ✅",
            "The 'bisect' module: Binary search for people who can't sort manually 📈",
            "Python's 'heapq': Priority queues that nobody understands 🏔️",
            "The 'secrets' module: Random numbers that are actually random! 🔐",
            "Python's 'contextlib': Custom context managers for control freaks 🎪",
            "The 'operator' module: Functions for operators, because why not? ➕",
            "Python's 'weakref': References that give up easily 🗑️",
            "The 'copy' module: For when assignment isn't confusing enough 📋",
            "Python's 'pickle' serializes almost any Python object: Security nightmare included! 🥒",
            "The 'json' module is faster than pickle: Only took 20 years to realize! ⚡",
            "Python's 'logging' module has 5 severity levels: DEBUG, INFO, WARNING, ERROR, PANIC 📝",
            "The 'unittest.mock' module: For when your code is too coupled to test 🎭",
            "Python's 'doctest': Tests disguised as documentation! Sneaky! 📖",
            "The 'pdb' debugger: import pdb; pdb.set_trace() - the print() of debugging 🐞",
            "Python's 'timeit' module: For when you need to prove your code is slow ⏱️",
            "The 'profile' module: Finds bottlenecks you didn't know you created 🚧",
            "Python's 'sys.getsizeof()': Shows how much memory you're wasting 📏",
            "The 'gc' module: Controls garbage collection, unlike your code quality 🗑️",
            "Python's 'inspect' module examines live objects! 🔍",
            "The 'ast' module parses Python source into syntax trees! 🌳",
            "Python's 'dis' module disassembles bytecode! 🔧",
            "The 'keyword' module lists Python's reserved words! 📝",
            "Python's 'tokenize' module breaks source into tokens! 🎫",
            "The 'textwrap' module formats text paragraphs! 📄",
            "Python's 're' module supports named capture groups! 🎯",
            "The 'string' module has useful constants like ascii_letters! 🔤",
            "Python's 'random' module can shuffle lists in-place! 🎲",
            "The 'statistics' module calculates mean, median, mode! 📊",
            "Python's 'decimal' module provides exact decimal arithmetic! 💯",
            "The 'fractions' module handles rational numbers perfectly! ➗",
            "Python's 'math' module has constants like pi and e! 🥧",
            "The 'cmath' module handles complex numbers! 🔢",
            "Python's 'datetime' module can parse ISO format automatically! 📅",
            "The 'calendar' module can generate text calendars! 📆",
            "Python's 'time' module measures both CPU and wall time! ⏰",
            "The 'locale' module handles internationalization! 🌍",
            "Python's 'gettext' module supports multiple languages! 🗣️",
            "The 'unicodedata' module provides Unicode character info! 🔤",
            "Python's 'base64' module encodes binary data as text! 📊",
            "The 'hashlib' module supports many hash algorithms! #️⃣",
            "Python's 'hmac' module creates secure message digests! 🔒",
            "The 'ssl' module handles secure socket connections! 🔐",
            "Python's 'super()' function: For when inheritance gets confusing! 👪",
            "The 'property' decorator: Getters and setters, but make it Pythonic! 🏠",
            "Python's 'slots' can save memory: Finally, optimization that works! 💾",
            "The '__new__' method runs before '__init__': Constructor inception! 🏗️",
            "Python's 'metaclasses' are classes that create classes: Mind blown! 🤯",
            "The 'classmethod' decorator: When 'self' isn't enough! 🎭",
            "Python's 'staticmethod': Methods that forgot they're in a class! 🤷‍♂️",
            "The 'abstractmethod' decorator: For methods that refuse to work! 🚫",
            "Python's 'namedtuple': Tuples with an identity crisis! 🏷️",
            "The 'defaultdict' never raises KeyError: Finally, a forgiving dictionary! 🤝",
            "Python's 'ChainMap': Multiple dictionaries pretending to be one! ⛓️",
            "The 'OrderedDict' maintains insertion order: Before it was cool! 📋",
            "Python's 'deque' is pronounced 'deck': Double-ended queue confusion! 🃏",
            "The 'Counter' class counts things: Revolutionary concept! 🔢",
            "Python's 'UserDict' lets you subclass dict properly! 👤",
            "The 'UserList' and 'UserString' exist too: Consistency! 📝",
            "Python's 'SimpleNamespace' is like a class without methods! 📦",
            "The 'types' module creates types dynamically: Type inception! 🏭",
            "Python's 'typing.Union' became '|' in 3.10: Progress! ➡️",
            "The 'typing.Literal' restricts values to specific literals! 🎯",
            "Python's 'typing.TypedDict' adds types to dictionaries! 📚",
            "The 'typing.Protocol' enables structural subtyping! 🏗️",
            "Python's 'typing.Generic' creates generic classes! 🧬",
            "The 'typing.Final' prevents reassignment: Immutability at last! 🔒",
            "Python's 'typing.ClassVar' marks class variables! 🏷️",
            "The '@overload' decorator provides multiple signatures! 📝",
            "Python's 'match' statement: Switch statements, but better! 🔄",
            "The walrus operator ':=' assigns and returns: Efficiency! 🦭",
            "Python's f-strings support '=' for debugging: f'{var=}' shows name and value! 🐛",
            "The 'breakpoint()' function calls the debugger: Built-in debugging! 🔍",
            "Python's '__future__' imports bring tomorrow's features today! 🚀",
            "The 'warnings' module helps deprecate features gracefully! ⚠️",
            "Python's 'traceback' module formats exceptions beautifully! 📋",
            "The 'linecache' module caches file lines for tracebacks! 💾",
            "Python's 'code' module provides interactive interpreters! 💻",
            "The 'codeop' module compiles code interactively! ⚙️",
            "Python's 'compileall' precompiles .py files to .pyc! 📦",
            "The 'py_compile' module compiles single files! 🔧",
            "Python's 'importlib' lets you import modules programmatically! 📥",
            "The 'pkgutil' module provides package utilities! 📦",
            "Python's 'modulefinder' finds module dependencies! 🔍",
            "The 'runpy' module runs Python modules as scripts! 🏃‍♂️",
            "Python's 'site' module handles site-packages! 📍",
            "The 'sysconfig' module provides build-time configuration! ⚙️",
            "Python's 'platform' module identifies the system! 🖥️",
            "The 'subprocess' module spawns new processes! 🍼",
            "Python's 'threading' module provides thread-based parallelism! 🧵",
            "The 'multiprocessing' module enables true parallelism! 🔀",
            "Python's 'concurrent.futures' simplifies parallel execution! ⚡",
            "The 'queue' module provides thread-safe queues! 📬",
            "Python's 'select' module waits for I/O completion! ⏳",
            "The 'selectors' module provides high-level I/O multiplexing! 🎛️",
            "Python's 'socket' module provides low-level networking! 🔌",
            "The 'socketserver' module creates network servers! 🖥️",
            "Python's 'http' package handles HTTP protocols! 🌐",
            "The 'urllib' package parses URLs and fetches data! 🔗",
            "Python's 'email' package handles email messages! 📧",
            "The 'smtplib' module sends emails via SMTP! 📮",
            "Python's 'poplib' and 'imaplib' retrieve emails! 📬",
            "The 'ftplib' module handles FTP connections! 📁",
            "Python's 'telnetlib' provides Telnet client functionality! 📞",
            "The 'xmlrpc' package implements XML-RPC! 🔄",
            "Python's 'sqlite3' module provides SQLite database access! 🗄️",
            "The 'dbm' package provides simple database interfaces! 📊",
            "Python's 'csv' module reads and writes CSV files! 📈",
            "The 'configparser' module handles configuration files! ⚙️",
            "Python's 'fileinput' module iterates over multiple files! 📄",
            "The 'tempfile' module creates temporary files safely! 🗂️",
            "Python's 'glob' module finds files using wildcards! 🔍",
            "The 'fnmatch' module matches filenames with patterns! 🎯",
            "Python's 'shutil' module provides high-level file operations! 📁",
            "The 'zipfile' module creates and extracts ZIP archives! 🗜️",
            "Python's 'tarfile' module handles TAR archives! 📦",
            "The 'gzip' module compresses and decompresses files! 🗜️",
            "Python's 'bz2' module provides bzip2 compression! 📦",
            "The 'lzma' module handles LZMA compression! 🗜️",
            "Python's 'zlib' module provides zlib compression! 📦",
            "The 'wave' module reads and writes WAV audio files! 🎵",
            "Python's 'audioop' module manipulates audio data! 🎶",
            "The 'chunk' module reads IFF chunked data! 🧩",
            "Python's 'colorsys' module converts between color systems! 🌈",
            "The 'imghdr' module determines image file types! 🖼️",
            "Python's 'sndhdr' module determines sound file types! 🔊",
            "The 'ossaudiodev' module provides OSS audio device access! 🔊",
            "Python's 'getopt' module parses command line options! ⌨️",
            "The 'argparse' module creates user-friendly command-line interfaces! 💻",
            "Python's 'optparse' module is deprecated but still works! ⚠️",
            "The 'shlex' module parses shell-like syntax! 🐚",
            "Python's 'cmd' module creates line-oriented command interpreters! 💻",
            "The 'readline' module provides line editing and history! ✏️",
            "Python's 'rlcompleter' module provides tab completion! ⭐",
            "The 'turtle' module provides turtle graphics! 🐢",
            "Python's 'tkinter' module creates GUI applications! 🖼️",
            "The 'tkinter.ttk' module provides themed widgets! 🎨",
            "Python's 'idle' is built with tkinter! 💻",
            "The 'pydoc' module generates documentation! 📚",
            "Python's 'doctest' finds bugs in docstrings! 🐛",
            "The 'unittest.mock' module creates test doubles! 🎭",
            "Python's 'venv' module creates virtual environments! 🏠",
            "The 'ensurepip' module bootstraps pip! 📦",
            "Python's 'pip' isn't actually part of the standard library! 📦",
            "The 'distutils' module is deprecated: Use setuptools instead! ⚠️",
            "Python's '__pycache__' directories store bytecode! 💾",
            "The '.pyc' files are compiled Python bytecode! ⚙️",
            "Python's bytecode is stack-based! 📚",
            "The 'dis' module shows you the bytecode! 👀",
            "Python's interpreter is written in C! It must be rewritten in Rust! 🔧",
            "PyPy is a Python interpreter written in Python! 🐍",
            "Jython runs Python on the JVM! ☕",
            "IronPython runs Python on .NET! 🔩",
            "MicroPython runs on microcontrollers! 🤖",
            "CircuitPython is MicroPython for education! 🎓",
            "Brython runs Python in web browsers! 🌐",
            "Pyodide brings Python to WebAssembly! 🕸️",
            "Python 2 reached end-of-life on January 1, 2020! ⚰️",
            "Python 3.12 has better error messages! 📝",
            "Python 3.11 is up to 60% faster than 3.10! 🏃‍♂️",
            "Python 3.10 added structural pattern matching! 🔄",
            "Python 3.9 made dict union operators official! ➕",
            "Python 3.8 introduced the walrus operator! 🦭",
            "Python 3.7 made dictionaries ordered by default! 📋",
            "Python 3.6 introduced f-strings! 🎯",
            "Python 3.5 added async/await syntax! ⚡",
            "Python uses reference counting for memory management! 🔢",
            "The GIL prevents true multithreading in CPython! 🔒",
            "Python's garbage collector handles circular references! ♻️",
            "The 'with' statement implements the context manager protocol! 🚪",
            "Python's 'for' loop calls '__iter__' and '__next__'! 🔄",
            "The 'in' operator calls '__contains__' method! 📦",
            "Python's '+' operator calls '__add__' method! ➕",
            "You can override almost any operator in Python! ⚙️",
            "Python's 'is' checks object identity, not equality! 🆔",
            "The 'None' object is a singleton in Python! 1️⃣",
            "Python's 'True' and 'False' are also singletons! ✅",
            "Small integers (-5 to 256) are cached in CPython! 💾",
            "Python strings are immutable objects! 🔒",
            "String concatenation creates new objects each time! 🔄",
            "Use 'join()' for efficient string concatenation! ⚡",
            "Python lists are actually dynamic arrays! 📊",
            "List comprehensions are faster than equivalent loops! 🏃‍♂️",
            "Python sets use hash tables for O(1) lookup! #️⃣",
            "Dictionary keys must be hashable objects! 🔑",
            "Python tuples are immutable but can contain mutable objects! 🧊",
            "The 'frozenset' is an immutable version of set! ❄️",
            "Python's 'range' objects are lazy and memory-efficient! 💤",
            "The 'enumerate' function adds indices to iterables! 🔢",
            "Python's 'zip' stops at the shortest iterable! 🤐",
            "Use 'itertools.zip_longest' for different-length iterables! 📏",
            "Python's 'map' and 'filter' return iterators, not lists! 🗺️",
            "List slicing creates shallow copies! 📋",
            "The 'copy' module provides deep and shallow copying! 📄",
            "Python's 'id()' function returns object memory address! 📍",
            "The 'hash()' function returns object hash values! #️⃣",
            "Python's 'len()' calls the '__len__' method! 📏",
            "The 'str()' function calls '__str__' or '__repr__'! 📝",
            "Python's 'repr()' should return unambiguous representations! 🔍",
            "The 'bool()' function calls '__bool__' or '__len__'! ✅",
            "Python considers empty containers as False! 📦",
            "The number 0 and None are also falsy in Python! 0️⃣",
            "Everything else is truthy in Python! ✨"
        ]
        
        # Shuffle the facts array for variety on each run
        import random
        random.shuffle(python_facts)
        
        def progress_callback(status):
            """Progress callback with comprehensive status handling"""
            nonlocal poll_count
            
            # Handle all possible API statuses
            if status == "failed":
                progress.update(
                    main_task,
                    description="[bold bright_red]❌ Generation failed - preparing error details...[/bold bright_red]",
                    completed=100
                )
                return
            elif status == "completed":
                # Handle completed status (should be handled by stages, but just in case)
                if "completed" in stages:
                    stage = stages["completed"]
                    progress.update(
                        main_task,
                        description=f"[{stage['color']}]{stage['icon']} {stage['desc']}[/{stage['color']}]",
                        completed=100
                    )
                return
            elif status == "timeout":
                progress.update(
                    main_task,
                    description="[bold bright_red]⏰ Request timed out - check your connection[/bold bright_red]",
                    completed=100
                )
                return
            elif status == "unknown":
                progress.update(
                    main_task,
                    description="[bold bright_yellow]❓ Unknown status - continuing to poll...[/bold bright_yellow]",
                    completed=50
                )
                return
            elif status in ["error", "network_error", "connection_error"]:
                progress.update(
                    main_task,
                    description="[bold bright_red]🌐 Network error - retrying connection...[/bold bright_red]",
                    completed=25
                )
                return
            
            # Handle known stages
            if status in stages:
                stage = stages[status]
                
                # For processing stage, show realistic polling progress
                if status == "processing":
                    poll_count += 1
                    # Calculate realistic progress based on polling
                    base_progress = 30  # Start at 30% when processing begins
                    poll_progress = min(40, (poll_count / max_polls) * 40)  # Up to 40% more from polling
                    actual_progress = base_progress + poll_progress
                    
                    # Get a fun Python fact for this poll
                    fact_index = (poll_count - 1) % len(python_facts)
                    current_fact = python_facts[fact_index]
                    
                    progress.update(
                        main_task,
                        description=f"[{stage['color']}]{stage['icon']} {stage['desc']} (Poll #{poll_count}/96)[/{stage['color']}]",
                        completed=actual_progress
                    )
                    
                    # Show the Python fact below the progress bar
                    self.console.print(f"[dim bright_blue]💡 Did you know? {current_fact}[/dim bright_blue]")
                else:
                    # Smooth animation for other stages
                    current = progress.tasks[main_task].completed
                    target = stage['progress']
                    
                    steps = max(1, int((target - current) / 2))
                    for i in range(steps):
                        intermediate = current + ((target - current) * (i + 1) / steps)
                        progress.update(
                            main_task,
                            description=f"[{stage['color']}]{stage['icon']} {stage['desc']}[/{stage['color']}]",
                            completed=intermediate
                        )
                        time.sleep(0.05)
                    
                    # Final update
                    progress.update(
                        main_task,
                        description=f"[{stage['color']}]{stage['icon']} {stage['desc']}[/{stage['color']}]",
                        completed=target
                    )
            else:
                # Handle any other unexpected status
                progress.update(
                    main_task,
                    description=f"[bold bright_magenta]🔄 Status: {status} - continuing to monitor...[/bold bright_magenta]",
                    completed=min(80, progress.tasks[main_task].completed + 5)
                )
        
        
        # Enhanced progress display with multiple columns
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(
                bar_width=60,
                complete_style="bright_green",
                finished_style="bold bright_green"
            ),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("•"),
            TimeElapsedColumn(),
            console=self.console,
            transient=False,
            expand=True
        ) as progress:
            
            # Start with beautiful initial state
            main_task = progress.add_task(
                f"[bright_blue]🎯 {stages['initializing']['desc']}[/bright_blue]",
                total=100,
                completed=0
            )
            
            # Smooth startup animation
            for i in range(stages['initializing']['progress']):
                progress.update(main_task, completed=i + 1)
                time.sleep(0.02)
            
            # Analysis phase with smooth transition
            progress_callback("analyzing")
            time.sleep(0.4)
            
            # Run the actual generation
            result = self.test_service.generate_test_for_method(selected_method, file_path, progress_callback)
            
            # Clean completion sequence
            if result.get('success'):
                progress_callback("finalizing")
                time.sleep(0.3)
                progress_callback("completed")
                time.sleep(0.5)  # Brief pause to show completion
            else:
                # Error state with clear indication and helpful message
                error_msg = result.get('error', 'Unknown error')
                progress.update(
                    main_task,
                    description=f"[bold bright_red]❌ Generation failed: {str(error_msg)[:50]}{'...' if len(str(error_msg)) > 50 else ''}[/bold bright_red]",
                    completed=100
                )
                time.sleep(1)  # Let user see the error
        
        self.console.print()
        
        # Clean completion status
        if result.get('success'):
            # Simple success message
            success_content = Text("Generation completed successfully", style="bold bright_green")
            success_panel = Panel(
                Align.center(success_content),
                title="[bold bright_green]✅ Complete[/bold bright_green]",
                border_style="bright_green",
                padding=(0, 2)
            )
            self.console.print(success_panel)
            
        else:
            # Clean error display
            error_content = Text("Generation failed", style="bold bright_red")
            error_panel = Panel(
                Align.center(error_content),
                title="[bold bright_red]❌ Failed[/bold bright_red]",
                border_style="bright_red",
                padding=(0, 2)
            )
            self.console.print(error_panel)
        
        return result

    def _count_test_methods(self, test_file_path):
        """Count the number of actual test cases using pytest collection (matches pytest output)"""
        try:
            import subprocess
            from pathlib import Path

            # Convert to absolute path to ensure file can be found
            file_path = Path(test_file_path).resolve()

            # Check if file exists
            if not file_path.exists():
                print(f"Warning: Test file not found at {file_path}")
                return 0

            # Use pytest --collect-only to get accurate test count (including parametrized tests)
            # Try to find pytest in common locations
            pytest_cmd = None
            for cmd_path in ["pytest", "./venv/bin/pytest"]:
                try:
                    subprocess.run([cmd_path, "--version"], capture_output=True, timeout=5)
                    pytest_cmd = [cmd_path]
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            # Try python -m pytest as fallback
            if not pytest_cmd:
                try:
                    subprocess.run(["python", "-m", "pytest", "--version"], capture_output=True, timeout=5)
                    pytest_cmd = ["python", "-m", "pytest"]
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass

            if not pytest_cmd:
                # Fallback to Rust method if pytest not found
                import tng_python
                count = tng_python.count_test_methods(str(file_path))
                return count

            result = subprocess.run(
                pytest_cmd + ["--collect-only", "-q", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')

                # First, try to find the summary line format: "filename: count"
                # This works with -q flag: "tests/20250922170046_test_save_test_file.py: 44"
                for line in lines:
                    line = line.strip()
                    if '.py:' in line and line.split(':')[-1].strip().isdigit():
                        # Extract number from "filename: 44" format
                        parts = line.split(':')
                        if len(parts) >= 2:
                            count_str = parts[-1].strip()
                            try:
                                return int(count_str)
                            except ValueError:
                                continue

                # Fallback: count individual test lines (verbose output)
                test_count = 0
                for line in lines:
                    line = line.strip()
                    # Count lines that contain test collection info
                    if '::' in line and ('test_' in line or 'Test' in line):
                        # Skip summary lines
                        if not any(skip in line.lower() for skip in ['collected', 'test session', 'platform', 'rootdir', 'plugins']):
                            test_count += 1

                # If still no tests found, try to count from collected summary
                if test_count == 0:
                    for line in lines:
                        if 'collected' in line.lower():
                            # Look for pattern like "collected 5 items"
                            import re
                            match = re.search(r'collected (\d+) items?', line.lower())
                            if match:
                                test_count = int(match.group(1))
                                break

                return test_count if test_count > 0 else 1  # At least 1 if file exists
            else:
                # Fallback to Rust method if pytest collection fails
                import tng_python
                count = tng_python.count_test_methods(str(file_path))
                return count

        except subprocess.TimeoutExpired:
            print(f"Timeout counting tests in {test_file_path}")
            return self._fallback_count_test_methods(test_file_path)
        except Exception as e:
            # Better error reporting for debugging
            print(f"Error counting test methods in {test_file_path}: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: try to count manually with Python
            return self._fallback_count_test_methods(test_file_path)

    def _fallback_count_test_methods(self, test_file_path):
        """Fallback method to count test methods using Python AST"""
        try:
            import ast
            from pathlib import Path

            file_path = Path(test_file_path).resolve()
            if not file_path.exists():
                return 0

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            count = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    count += 1

            return count
        except Exception as e:
            print(f"Fallback count also failed for {test_file_path}: {e}")
            return 0

    def _show_run_command_menu(self, test_file_path):
        """Show the run command and a menu with options"""
        from pathlib import Path
        from rich.syntax import Syntax
        from ..config import get_config
        
        test_path = Path(test_file_path)
        
        # Get user's configured test framework
        try:
            config = get_config()
            test_framework = getattr(config, 'TEST_FRAMEWORK', 'pytest').lower()
        except:
            test_framework = 'pytest'  # fallback
        
        # Determine run command based on configured test framework with minimal output
        if test_framework == 'unittest':
            # Convert file path to module path for unittest - quiet mode
            module_path = str(test_path).replace('/', '.').replace('.py', '')
            run_command = f"python -m unittest {module_path} -q"
        elif test_framework == 'pytest':
            # Use pytest with ultra-minimal output: count dots and F's
            run_command = f"pytest {test_file_path} -q --tb=no --no-summary --no-header"
        elif test_framework == 'nose2':
            # Use nose2 with quiet mode
            run_command = f"nose2 -s {test_path.parent} {test_path.stem} -q"
        else:
            # Default to pytest for unknown frameworks
            run_command = f"pytest {test_file_path} -q --tb=no --no-summary --no-header"
        
        if run_command:
            self.console.print()
            
            # Create command display
            command_syntax = Syntax(run_command, "bash", theme="monokai", background_color="default")
            
            command_panel = self.create_centered_panel(
                command_syntax, 
                f"{self.theme.Icons.TERMINAL} Run Tests"
            )
            self.console.print(command_panel)
            self.console.print()
            
            # Show menu options
            menu_choices = [
                questionary.Choice(f"{self.theme.Icons.TERMINAL} Run tests now", "run"),
                questionary.Choice(f"{self.theme.Icons.GENERATE} Generate more tests", "generate"),
                questionary.Choice(f"{self.theme.Icons.BACK} Back to Main Menu", "main")
            ]
            
            choice = questionary.select(
                self.theme.Messages.SELECT_OPTION,
                choices=menu_choices,
                style=self.get_common_style()
            ).ask()
            
            if choice == "run":
                return self._run_tests_command(run_command)
            elif choice == "generate":
                return self._show_file_selection()
            else:  # main or None
                return "back"
        else:
            self.press_any_key()
            return "back"
    
    def _run_tests_command(self, command):
        """Run the test command and show results"""
        import subprocess
        from ..config import get_config
        
        self.console.print()
        
        # Show running status
        running_text = Text(
            f"{self.theme.Icons.LOADING} Running: {command}",
            style=self.theme.format_bold_message("info")
        )
        running_panel = self.create_centered_panel(running_text, f"{self.theme.Icons.TERMINAL} Executing Tests")
        self.console.print(running_panel)
        self.console.print()
        
        try:
            # Run the command
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Get test framework for parsing
            try:
                config = get_config()
                framework = getattr(config, 'TEST_FRAMEWORK', 'pytest').lower()
            except:
                framework = 'pytest'
            
            # Parse test results to extract pass/fail counts
            passed, failed, total = self._parse_test_results(result.stdout, result.stderr, framework)
            
            # Show simple results summary
            if result.returncode == 0:
                success_text = Text(
                    f"{self.theme.Icons.SUCCESS} All tests passed! ({passed}/{total})",
                    style=self.theme.format_bold_message("success")
                )
                success_panel = self.create_centered_panel(success_text, "✅ Test Results")
                self.console.print(success_panel)
            else:
                if failed > 0:
                    warning_text = Text(
                        f"{self.theme.Icons.WARNING} {passed} passed, {failed} failed ({total} total)",
                        style=self.theme.format_bold_message("warning")
                    )
                    warning_panel = self.create_centered_panel(warning_text, "⚠️ Test Results")
                    self.console.print(warning_panel)
                else:
                    # Error running tests (not test failures)
                    error_text = Text(
                        f"{self.theme.Icons.ERROR} Error running tests",
                        style=self.theme.format_bold_message("error")
                    )
                    error_panel = self.create_centered_panel(error_text, "❌ Test Error")
                    self.console.print(error_panel)
            
            # No need to show raw output anymore - we parse it directly
                
        except subprocess.TimeoutExpired:
            timeout_text = Text(
                f"{self.theme.Icons.WARNING} Test execution timed out (60s limit)",
                style=self.theme.format_bold_message("warning")
            )
            timeout_panel = self.create_centered_panel(timeout_text, "⏰ Timeout")
            self.console.print(timeout_panel)
            
        except FileNotFoundError:
            error_text = Text(
                f"{self.theme.Icons.ERROR} Command not found: {command.split()[0]}",
                style=self.theme.format_bold_message("error")
            )
            error_panel = self.create_centered_panel(error_text, "❌ Command Error")
            self.console.print(error_panel)
            
        except Exception as e:
            error_text = Text(
                f"{self.theme.Icons.ERROR} Failed to run tests: {str(e)}",
                style=self.theme.format_bold_message("error")
            )
            error_panel = self.create_centered_panel(error_text, "❌ Execution Error")
            self.console.print(error_panel)
        
        self.press_any_key()
        return "back"
    
    def _parse_test_results(self, stdout, stderr, framework):
        """Parse test output to extract pass/fail counts"""
        import re
        
        passed = 0
        failed = 0
        total = 0
        
        output = stdout + stderr
        
        if framework == 'pytest':
            # Count dots (.) for passed tests and F for failed tests
            passed = output.count('.')
            failed = output.count('F')
            # Also count other failure indicators
            failed += output.count('E')  # Errors
            failed += output.count('s')  # Skipped (treat as not-passed)
            total = passed + failed
                
        elif framework == 'unittest':
            # Look for unittest summary like "Ran 3 tests in 0.001s" and "OK" or "FAILED"
            ran_match = re.search(r'Ran (\d+) tests?', output)
            if ran_match:
                total = int(ran_match.group(1))
                
            if 'OK' in output and 'FAILED' not in output:
                passed = total
                failed = 0
            else:
                # Look for failure count like "FAILED (failures=2)"
                fail_match = re.search(r'failures=(\d+)', output)
                error_match = re.search(r'errors=(\d+)', output)
                
                failed = 0
                if fail_match:
                    failed += int(fail_match.group(1))
                if error_match:
                    failed += int(error_match.group(1))
                    
                passed = total - failed
                
        elif framework == 'nose2':
            # Similar to unittest but different format
            ran_match = re.search(r'Ran (\d+) tests?', output)
            if ran_match:
                total = int(ran_match.group(1))
                
            if 'OK' in output:
                passed = total
                failed = 0
            else:
                failed = len(re.findall(r'FAIL|ERROR', output))
                passed = total - failed
        
        # Ensure we have reasonable values
        if total == 0 and (passed > 0 or failed > 0):
            total = passed + failed
            
        return passed, failed, total

