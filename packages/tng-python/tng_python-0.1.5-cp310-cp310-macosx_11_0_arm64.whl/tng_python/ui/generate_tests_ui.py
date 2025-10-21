from pathlib import Path

from .go_ui_session import GoUISession
from ..service import GenerateTestService


class GenerateTestsUI:
    def __init__(self):
        self.test_service = GenerateTestService()
        self.go_ui_session = GoUISession()
        self.go_ui_session.start()
    
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
        python_files = self._get_user_python_files()
        
        if not python_files:
            self.go_ui_session.show_no_items("Python files")
            return "back"
        
        items = [
            {"name": file.name, "path": str(file.parent)}
            for file in python_files
        ]

        selected_name = self.go_ui_session.show_list_view("Select Python File", items)

        if selected_name == "back":
                return "back"
            
        selected_file = None
        for file in python_files:
            if file.name == selected_name:
                    selected_file = str(file)
                    break

        if not selected_file:
                return "back"
        
        return self._show_methods_for_file(selected_file)

    def _show_methods_for_file(self, file_path):
        """Show methods for a specific file"""
        methods = self._get_file_methods(file_path)
        
        if not methods:
            self.go_ui_session.show_no_items("methods")
            return self._show_file_selection()
        
        file_name = Path(file_path).name
        items = [{"name": method, "path": f"Method in {file_name}"} for method in methods]

        selected_method = self.go_ui_session.show_list_view(f"Select Method for {file_name}", items)

        if selected_method == "back":
                return self._show_file_selection()
        
        if selected_method:
            result = self._generate_tests_for_method(file_path, selected_method)
            if result and result.get('file_path') and not result.get('error'):
                self._show_post_generation_menu(result)
            return self._show_file_selection()
        else:
            return self._show_file_selection()

    def _generate_tests_for_method(self, file_path, selected_method):
        """Generate tests for selected method using Go UI progress"""
        file_name = Path(file_path).name
        
        def progress_handler(progress):
            progress.update("Submitting request to API...")
            
            # Progress callback that receives status messages and percentage from service
            def handle_progress(message, percent=None):
                if isinstance(message, str):
                    progress.update(message, percent)
            
            gen_result = self.test_service.generate_test_for_method(
                selected_method, 
                file_path,
                progress_callback=handle_progress
            )

            if gen_result and gen_result.get('error'):
                progress.error("Test generation failed. Please try again.")
                return {"result": gen_result}
            elif gen_result and gen_result.get('success'):
                progress.update("Saving test file...")
                file_info = self.test_service.save_test_file(gen_result.get('result', ''))

                if file_info:
                    test_count = self._count_test_methods(file_info.get('absolute_path', ''))
                    count_msg = "1 test" if test_count == 1 else f"{test_count} tests"

                    elapsed = gen_result.get('elapsed', 0)
                    time_msg = f" in {elapsed:.1f}s" if elapsed > 0 else ""

                    return {
                        "message": f"Generated {count_msg}{time_msg}!",
                        "result": file_info
                    }
                else:
                    progress.error("Failed to save test file")
                    return {"result": {"error": "Failed to save test file"}}
            else:
                progress.error("Test generation failed. Please try again.")
                return {"result": {"error": "Unknown error"}}

        result = self.go_ui_session.show_progress(
            f"Generating test for {file_name}#{selected_method}",
            progress_handler
        )

        if result and result.get('result') and not result['result'].get('error'):
            return result['result']
        return None

    def _show_post_generation_menu(self, file_info):
        """Show post-generation menu (like Ruby implementation)"""
        file_path = file_info.get('file_path') or file_info.get('absolute_path')
        run_command = file_info.get('run_command', f'pytest {file_path}')

        while True:
            choice = self.go_ui_session.show_post_generation_menu(file_path, run_command)

            if choice == "run_tests":
                self._run_and_show_test_results(run_command)
            elif choice == "copy_command":
                self._copy_command_and_show_success(run_command)
            elif choice == "back":
                break
            else:
                break

    def _copy_command_and_show_success(self, command):
        """Copy command to clipboard and show success"""
        import subprocess
        import sys

        try:
            if sys.platform == 'darwin':  # macOS
                subprocess.run(['pbcopy'], input=command.encode('utf-8'), check=True)
                self.go_ui_session.show_clipboard_success(command)
            elif sys.platform.startswith('linux'):  # Linux
                try:
                    subprocess.run(['xclip', '-selection', 'clipboard'],
                                   input=command.encode('utf-8'), check=True)
                    self.go_ui_session.show_clipboard_success(command)
                except FileNotFoundError:
                    print(f"\n📋 Copy this command:\n{command}\n")
                    input("Press Enter to continue...")
            else:  # Windows or other
                print(f"\n📋 Copy this command:\n{command}\n")
                input("Press Enter to continue...")
        except Exception as e:
            print(f"\n📋 Copy this command:\n{command}\n")
            input("Press Enter to continue...")

    def _run_and_show_test_results(self, command):
        """Run tests and show results using Go UI"""
        import subprocess

        # Run tests with spinner
        def spinner_handler():
            output = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            return {
                "success": True,
                "message": "Tests completed",
                "output": output.stdout + output.stderr,
                "exit_code": output.returncode
            }

        test_output = self.go_ui_session.show_spinner("Running tests...", spinner_handler)

        passed, failed, errors, total = self._parse_test_output(
            test_output.get('output', ''),
            test_output.get('exit_code', 1)
        )

        self.go_ui_session.show_test_results(
            "Test Results",
            passed,
            failed,
            errors,
            total,
            []  # No detailed results for now
        )

    def _parse_test_output(self, output, exit_code):
        """Parse pytest output to extract test counts"""
        import re

        passed = failed = errors = 0

        passed_match = re.search(r'(\d+) passed', output)
        failed_match = re.search(r'(\d+) failed', output)
        error_match = re.search(r'(\d+) error', output)

        if passed_match:
            passed = int(passed_match.group(1))
        if failed_match:
            failed = int(failed_match.group(1))
        if error_match:
            errors = int(error_match.group(1))

        total = passed + failed + errors

        if total == 0:
            if exit_code == 0:
                passed = 1
                total = 1
            else:
                failed = 1
                total = 1

        return passed, failed, errors, total

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
            
        except Exception:
            return []

    def _count_test_methods(self, test_file_path):
        """Count the number of actual test cases using pytest collection (matches pytest output)"""
        try:
            import subprocess
            from pathlib import Path

            file_path = Path(test_file_path).resolve()

            if not file_path.exists():
                return 0

            pytest_cmd = None
            for cmd_path in ["pytest", "./venv/bin/pytest"]:
                try:
                    subprocess.run([cmd_path, "--version"], capture_output=True, timeout=5)
                    pytest_cmd = [cmd_path]
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            if not pytest_cmd:
                try:
                    subprocess.run(["python", "-m", "pytest", "--version"], capture_output=True, timeout=5)
                    pytest_cmd = ["python", "-m", "pytest"]
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass

            if not pytest_cmd:
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

                for line in lines:
                    line = line.strip()
                    if '.py:' in line and line.split(':')[-1].strip().isdigit():
                        parts = line.split(':')
                        if len(parts) >= 2:
                            count_str = parts[-1].strip()
                            try:
                                return int(count_str)
                            except ValueError:
                                continue

                test_count = 0
                for line in lines:
                    line = line.strip()
                    if '::' in line and ('test_' in line or 'Test' in line):
                        # Skip summary lines
                        if not any(skip in line.lower() for skip in
                                   ['collected', 'test session', 'platform', 'rootdir', 'plugins']):
                            test_count += 1

                if test_count == 0:
                    for line in lines:
                        if 'collected' in line.lower():
                            import re
                            match = re.search(r'collected (\d+) items?', line.lower())
                            if match:
                                test_count = int(match.group(1))
                                break

                return test_count if test_count > 0 else 1  # At least 1 if file exists
            else:
                import tng_python
                count = tng_python.count_test_methods(str(file_path))
                return count

        except subprocess.TimeoutExpired:
            return self._fallback_count_test_methods(test_file_path)
        except Exception:
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
        except Exception:
            return 0
