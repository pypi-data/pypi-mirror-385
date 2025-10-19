import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
from datetime import datetime
from ..config import get_api_key, get_enabled_config


class GenerateTestService:
    """
    Service for generating tests using the TNG API
    """
    
    def __init__(self):
        self.console = Console()
        from ..config import get_base_url
        base_url = get_base_url()
        self.submit_url = f"{base_url}/cli/tng_python/contents/generate_tests/"
        self.status_url_template = f"{base_url}/cli/tng_python/content_responses/{{job_id}}"
        
    def generate_test_for_method(self, method: str, file_path: str, progress_callback=None) -> Dict[str, Any]:
        """
        Generate test for a specific method using the Rust backend
        
        Args:
            method: Method name to generate tests for
            file_path: Path to the source file
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with success status and result/error
        """
        try:
            import tng_python
            
            # Get configuration
            user_config = get_enabled_config()
            if not user_config:
                return {
                    "success": False,
                    "error": "No configuration found. Please run configuration setup first."
                }
            
            api_key = get_api_key()
            if not api_key:
                return {
                    "success": False,
                    "error": "No API key found. Please configure your API key first."
                }
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": f"TNG-Python/{tng_python.__version__}",
                "Authorization": f"Bearer {get_api_key()}"
            }
                        
            dependency_content, dependency_filename = self._get_dependency_content()
            
            result = tng_python.send_async_job_request(
                submit_url=str(self.submit_url),
                status_url_template=str(self.status_url_template),
                headers=headers,
                file_path=str(file_path),
                method=method,
                user_config=user_config,
                dependency_content=dependency_content,
                dependency_filename=dependency_filename,
                progress_callback=progress_callback
            )
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Generation failed: {str(e)}"
            }

    def set_submit_url(self, url: str) -> None:
        """Set the submit URL for test generation"""
        self.submit_url = url
    
    def set_status_url_template(self, url_template: str) -> None:
        """Set the status URL template for polling"""
        self.status_url_template = url_template
    
    def save_test_file(self, test_content: str) -> Optional[Dict[str, Any]]:
        """
        Save test file from API response content
        
        Args:
            test_content: JSON string response from API
            
        Returns:
            Dictionary with file information or None if failed
        """
        try:            
            parsed_response = json.loads(test_content)
            
            if parsed_response.get("error"):
                self.console.print(f"❌ API responded with an error: {parsed_response['error']}", 
                                 style="bold red")
                return None
            
            # Validate required fields
            if not parsed_response.get("file_content"):
                self.console.print("❌ API response missing file_content field", 
                                 style="bold red")
                self.console.print(f"ℹ️ Response keys: {list(parsed_response.keys())}", 
                                 style="bold cyan")
                return None
            
            # Handle multiple possible field names for file path
            file_path = (parsed_response.get("test_file_path") or 
                        parsed_response.get("file_path") or 
                        parsed_response.get("file_name") or 
                        parsed_response.get("file"))
            
            if not file_path:
                self.console.print("❌ API response missing test_file_path or file_path field", 
                                 style="bold red")
                self.console.print(f"ℹ️ Response keys: {list(parsed_response.keys())}", 
                                 style="bold cyan")
                return None
 
            # Create directory if it doesn't exist and write file
            file_path_obj = Path(file_path)
            if not str(file_path_obj).startswith("tests/"):
                file_path_obj = Path("tests") / file_path_obj.name

            # Ensure Python test files have .py extension
            if not file_path_obj.name.endswith('.py'):
                # Replace any other extension with .py
                stem = file_path_obj.stem
                if '.' in stem:
                    # Handle cases like "test.rb" -> "test.py"
                    stem = stem.split('.')[0]
                file_path_obj = file_path_obj.parent / f"{stem}.py"
            
            # Add timestamp prefix if filename doesn't have one
            filename = file_path_obj.name
            if not self._has_timestamp_prefix(filename):
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                new_filename = f"{timestamp}_{filename}"
                file_path_obj = file_path_obj.parent / new_filename
            
            # Write the file
            try:
                file_path_obj.write_text(parsed_response["file_content"])
            except FileNotFoundError:
                # Create directory if it doesn't exist
                file_path_obj.parent.mkdir(parents=True, exist_ok=True)
                file_path_obj.write_text(parsed_response["file_content"])
            
            self.console.print("✅ Test generated successfully!", 
                             style="bold green")
            absolute_path = file_path_obj.resolve()
            
            # Run ruff validation on the saved file
            self._run_ruff_validation(str(absolute_path))
            
            self.console.print(f"📄 Please review the generated tests at: {file_path_obj}", 
                             style="bold cyan")
            
            
            return {
                "file_path": str(file_path_obj),  # Return actual saved path with timestamp
                "absolute_path": str(absolute_path),
                "test_class_name": parsed_response.get("test_class_name"),
                "method_name": parsed_response.get("method_name"),
                "framework": parsed_response.get("framework", "pytest")
            }
            
        except json.JSONDecodeError as e:
            self.console.print(f"❌ Failed to parse API response as JSON: {e}", 
                             style="bold red")
            self.console.print(f"📄 Raw response: {test_content[:200]}...", 
                             style="dim white")
            raise
        except Exception as e:
            self.console.print(f"❌ Failed to save test file: {e}", 
                             style="bold red")
            return None

    def get_test_frameworks(self) -> list:
        """Get list of supported test frameworks"""
        return ["pytest", "unittest"]
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate the current configuration"""
        config = get_enabled_config()
        api_key = get_api_key()
        
        issues = []
        if not config:
            issues.append("No configuration found")
        if not api_key:
            issues.append("No API key configured")
        if config and not config.get('base_url') and not config.get('submit_url'):
            issues.append("Base URL or Submit URL not configured")
            
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "config": config,
            "has_api_key": bool(api_key)
        }
    
    def _get_dependency_content(self) -> tuple:
        """Get dependency file content and filename based on user configuration"""
        try:
            from ..config import get_config
            config = get_config()
            if hasattr(config, 'DEPENDENCY_FILE') and config.DEPENDENCY_FILE:
                dep_file_path = Path(config.DEPENDENCY_FILE)
                if dep_file_path.exists():
                    content = dep_file_path.read_text(encoding='utf-8')
                    filename = dep_file_path.name
                    return content, filename
        except Exception as e:
            # Log error but don't fail the request
            print(f"Warning: Could not read dependency file: {e}")
        
        return None, None
    
    def _has_timestamp_prefix(self, filename: str) -> bool:
        """
        Check if filename has numeric prefix (any numbers followed by underscore)
        
        Args:
            filename: The filename to check
            
        Returns:
            True if filename starts with numbers and underscore
        """
        import re
        # Pattern: one or more digits followed by underscore at start of filename
        numeric_pattern = r'^\d+_'
        return bool(re.match(numeric_pattern, filename))
    
    def _run_ruff_validation(self, file_path: str) -> None:
        """
        Run ruff validation on the saved test file
        
        Args:
            file_path: Absolute path to the test file
        """
        try:
            # First run ruff check to see issues
            result = subprocess.run(
                ["ruff", "check", file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.console.print("✅ Ruff validation passed - no issues found", 
                                 style="bold green")
            else:
                self.console.print("⚠️  Ruff found some issues, attempting safe fixes...", 
                                 style="bold yellow")
                
                # Try to fix safe issues
                subprocess.run(
                    ["ruff", "check", "--fix", file_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # Run check again to see remaining issues
                final_result = subprocess.run(
                    ["ruff", "check", file_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if final_result.returncode == 0:
                    self.console.print("✅ Ruff auto-fixed all issues successfully!", 
                                     style="bold green")
                else:
                    self.console.print("⚠️  Some issues remain after auto-fix:", 
                                     style="bold yellow")
                    if final_result.stdout:
                        self.console.print(final_result.stdout, style="dim white")
                    
        except subprocess.TimeoutExpired:
            self.console.print("⚠️  Ruff validation timed out", style="bold yellow")
        except FileNotFoundError:
            self.console.print("ℹ️  Ruff not found - skipping validation", style="dim cyan")
        except Exception as e:
            self.console.print(f"⚠️  Ruff validation failed: {e}", style="bold yellow")
