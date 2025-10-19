#!/usr/bin/env python3
"""
TNG Python - Main CLI Entry Point using Typer
Much cleaner than manual argument preprocessing!
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich import print

from .interactive import TngInteractive
from .cli import init_config
from .service import GenerateTestService
from . import __version__
from .ui.theme import TngTheme
from .ui.options_ui import OptionsUI

# Create Typer app
app = typer.Typer(
    name="tng",
    help="TNG Python - LLM-Powered Test Generation for Python Applications",
    add_completion=False,
    rich_markup_mode="rich"
)

console = Console()


def find_python_file(file_arg: str) -> Path:
    """Find Python file based on argument"""
    current_dir = Path.cwd()
    
    # If it's already a full path, use it
    if file_arg.endswith('.py'):
        file_path = Path(file_arg)
        if file_path.exists():
            return file_path
        # Try relative to current directory
        file_path = current_dir / file_arg
        if file_path.exists():
            return file_path
    
    # Try with .py extension
    filename = file_arg if file_arg.endswith('.py') else f"{file_arg}.py"
    
    # Search in current directory first
    file_path = current_dir / filename
    if file_path.exists():
        return file_path
    
    # Search recursively in project
    for file_path in current_dir.rglob(filename):
        # Skip common exclude directories
        if any(excluded in file_path.parts for excluded in [
            'venv', 'env', '.venv', '.env', 'site-packages', 
            '__pycache__', '.git', 'node_modules', 'target', 'build', 'dist',
            'tests', 'test', 'spec'
        ]):
            continue
        return file_path
    
    raise FileNotFoundError(f"Could not find Python file: {file_arg}")


@app.command()
def generate(
    file: str = typer.Option(
        None, 
        "-f", "--file",
        help="File name or path to generate tests for"
    ),
    method: Optional[str] = typer.Option(
        None, 
        "-m", "--method",
        help="Specific method name to generate tests for"
    ),
):
    """Generate tests for Python files and methods"""
    
    if not file:
        print(f"[{TngTheme.Colors.ERROR}]{TngTheme.Icons.ERROR} Error: --file is required[/{TngTheme.Colors.ERROR}]")
        print("Use 'tng --help' for usage information")
        raise typer.Exit(1)
    
    try:
        # Find the file
        file_path = find_python_file(file)
        print(f"{TngTheme.Icons.SEARCH} Found file: {file_path}")
        
        # Get methods from file
        try:
            import tng_python
            analysis = tng_python.analyze_python_file(str(file_path))
            
            methods = []
            
            # Extract methods based on analysis
            if 'classes' in analysis and isinstance(analysis['classes'], dict):
                for class_name, class_info in analysis['classes'].items():
                    if isinstance(class_info, dict) and 'methods' in class_info:
                        for method_name, method_info in class_info['methods'].items():
                            if not method_name.startswith('_') or method_name == '__init__':
                                methods.append({
                                    'name': method_name,
                                    'class': class_name,
                                    'display': f"{class_name}.{method_name}",
                                    'type': 'method',
                                    'info': method_info
                                })
            
            if 'functions' in analysis and isinstance(analysis['functions'], dict):
                for func_name, func_info in analysis['functions'].items():
                    if not func_name.startswith('_'):
                        methods.append({
                            'name': func_name,
                            'class': None,
                            'display': func_name,
                            'type': 'function',
                            'info': func_info
                        })
            
            if not methods:
                print(f"[{TngTheme.Colors.WARNING}]{TngTheme.Icons.ERROR} No public methods found in {file_path.name}[/{TngTheme.Colors.WARNING}]")
                raise typer.Exit(1)
            
            # Filter by method name if specified
            if method:
                matching_methods = [
                    m for m in methods 
                    if m['name'].lower() == method.lower() or 
                       m['display'].lower() == method.lower()
                ]
                if not matching_methods:
                    print(f"[{TngTheme.Colors.ERROR}]{TngTheme.Icons.ERROR} Method '{method}' not found in {file_path.name}[/{TngTheme.Colors.ERROR}]")
                    print(f"Available methods: {', '.join([m['display'] for m in methods])}")
                    raise typer.Exit(1)
                methods = matching_methods
            
            # Generate tests
            test_service = GenerateTestService()
            
            print(f"{TngTheme.Icons.ROCKET} Generating tests for {len(methods)} method(s)...")
            
            for method_item in methods:
                print(f"  {TngTheme.Icons.WRITE} Processing: {method_item['display']}")
                result = test_service.generate_test_for_method(method_item['name'], str(file_path))
                
                if result.get('success'):
                    print(f"  [{TngTheme.Colors.SUCCESS}]{TngTheme.Icons.SUCCESS} Generated test for {method_item['display']}[/{TngTheme.Colors.SUCCESS}]")
                else:
                    print(f"  [{TngTheme.Colors.ERROR}]{TngTheme.Icons.ERROR} Failed to generate test for {method_item['display']}: {result.get('error', 'Unknown error')}[/{TngTheme.Colors.ERROR}]")
            
            print(f"[{TngTheme.Colors.SUCCESS}]{TngTheme.Icons.COMPLETE} Test generation completed![/{TngTheme.Colors.SUCCESS}]")
            
        except Exception as e:
            print(f"[{TngTheme.Colors.ERROR}]{TngTheme.Icons.ERROR} Error analyzing file: {str(e)}[/{TngTheme.Colors.ERROR}]")
            raise typer.Exit(1)

    except FileNotFoundError as e:
        print(f"[{TngTheme.Colors.ERROR}]{TngTheme.Icons.ERROR} {str(e)}[/{TngTheme.Colors.ERROR}]")
        raise typer.Exit(1)
    except Exception as e:
        print(f"[{TngTheme.Colors.ERROR}]{TngTheme.Icons.ERROR} Error: {str(e)}[/{TngTheme.Colors.ERROR}]")
        raise typer.Exit(1)


@app.command()
def interactive():
    """Launch interactive mode"""
    try:
        app = TngInteractive()
        app.show_main_menu()
    except KeyboardInterrupt:
        try:
            app = TngInteractive()
            app.exit_ui.show()
        except:
            print(f"\n[{TngTheme.Colors.WARNING}]{TngTheme.Icons.GOODBYE}[/{TngTheme.Colors.WARNING}]")
        raise typer.Exit(0)
    except Exception as e:
        print(f"[{TngTheme.Colors.ERROR}]{TngTheme.Icons.ERROR} Error: {str(e)}[/{TngTheme.Colors.ERROR}]")
        raise typer.Exit(1)


@app.command()
def init():
    """Generate TNG configuration file"""
    init_config()


@app.command()
def options():
    """Show all supported frameworks and options with interactive tables"""
    try:
        options_ui = OptionsUI()
        result = options_ui.show_main_options_menu()
        
        # Handle result actions
        if result == "generate_config":
            print(f"\n{TngTheme.Icons.CONFIG} Generating configuration...")
            init_config()
        elif result == "back":
            print(f"\n{TngTheme.Icons.GOODBYE} Thanks for exploring TNG options!")
            
    except KeyboardInterrupt:
        print(f"\n{TngTheme.Icons.GOODBYE} Goodbye!")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@app.command()
def show_frameworks():
    """Show supported web frameworks table"""
    try:
        options_ui = OptionsUI()
        options_ui.show_web_frameworks_table()
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@app.command()
def show_testing():
    """Show supported testing frameworks and tools"""
    try:
        options_ui = OptionsUI()
        options_ui.show_testing_frameworks_table()
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    file: Optional[str] = typer.Option(
        None, 
        "-f", "--file",
        help="File name or path to generate tests for"
    ),
    method: Optional[str] = typer.Option(
        None, 
        "-m", "--method", 
        help="Specific method name to generate tests for"
    ),
    version: bool = typer.Option(
        False, 
        "--version", "-v",
        help="Show version and exit"
    )
):
    """
    TNG Python - LLM-Powered Test Generation for Python Applications
    
    Examples:
    
        [bold]tng[/bold]                          # Interactive mode
        [bold]tng -f users.py[/bold]              # Generate tests for all methods in file  
        [bold]tng -f users.py -m save[/bold]      # Generate test for specific method
        [bold]tng init[/bold]                     # Generate configuration file
    
    You can also use short syntax:
    
        [bold]tng f=users.py m=save[/bold]        # Same as above but shorter!
    """
    
    if version:
        print(f"TNG Python version: {__version__}")
        raise typer.Exit()
    
    # If a subcommand was invoked, don't run the main logic
    if ctx.invoked_subcommand is not None:
        return
    
    # If file argument provided, run generate command
    if file:
        ctx.invoke(generate, file=file, method=method)
        return
    
    # Otherwise run interactive mode
    ctx.invoke(interactive)


if __name__ == "__main__":
    app()
