"""
Options UI - Interactive menu showing all supported frameworks and options
"""

from rich.table import Table
from rich.panel import Panel
import questionary
from .base_ui import BaseUI

class OptionsUI(BaseUI):
    """Interactive UI for browsing all TNG supported options"""
    
    def __init__(self):
        super().__init__()
        
    def show_main_options_menu(self):
        """Show the main options menu"""
        self.clear_screen()
        self.show_banner()
        
        # Main options menu
        options = [
            f"{self.theme.Icons.CODE}  Web Frameworks & Authentication",
            f"{self.theme.Icons.TEST}  Testing Frameworks & Tools", 
            f"{self.theme.Icons.BRAIN}  ML/AI Frameworks",
            f"{self.theme.Icons.FOLDER}  Database & ORM Options",
            f"{self.theme.Icons.EMAIL}  Email & Job Queue Options",
            f"{self.theme.Icons.LIGHTBULB}  Authentication Examples",
            f"{self.theme.Icons.CONFIG}   Generate Configuration",
            f"{self.theme.Icons.BACK}   Back to Main Menu"
        ]
        
        choice = questionary.select(
            "What would you like to explore?",
            choices=options,
            style=self.get_common_style()
        ).ask()
        
        if choice is None:
            return "back"
            
        if "Web Frameworks" in choice:
            return self.show_web_frameworks_table()
        elif "Testing Frameworks" in choice:
            return self.show_testing_frameworks_table()
        elif "ML/AI Frameworks" in choice:
            return self.show_ml_frameworks_table()
        elif "Database" in choice:
            return self.show_database_options_table()
        elif "Email" in choice:
            return self.show_email_job_options_table()
        elif "Authentication Examples" in choice:
            result = self.show_auth_examples()
            if result == "back":
                return self.show_main_options_menu()
            return result
        elif "Generate Configuration" in choice:
            return "generate_config"
        else:
            return "back"
    
    def show_web_frameworks_table(self):
        """Show comprehensive web frameworks table"""
        self.clear_screen()
        
        # Framework config options table
        table = Table(title="🌐 Web Framework Config Options", show_header=True, header_style="bold cyan")
        table.add_column("Config Setting", style="bold white", width=20)
        table.add_column("Available Options", style="green", width=50)
        
        frameworks_data = [
            ("FRAMEWORK", "django, flask, fastapi, tornado, sanic, pyramid, bottle, cherrypy, falcon, starlette, generic"),
            ("AUTHENTICATION_LIBRARY", "django-auth, django-allauth, djoser, flask-login, flask-security, fastapi-users, authlib, custom, none"),
            ("AUTHORIZATION_LIBRARY", "django-guardian, django-rules, flask-principal, casbin, fastapi-permissions, custom, none")
        ]
        
        for setting, options in frameworks_data:
            table.add_row(setting, options)
        
        self.console.print(table)
        self.console.print()
        
        # Authentication types table
        auth_table = Table(title="🔐 Authentication Config Options", show_header=True, header_style="bold green")
        auth_table.add_column("Config Setting", style="bold white", width=25)
        auth_table.add_column("Available Options", style="white", width=45)
        
        auth_types = [
            ("AUTHENTICATION_ENABLED", "True, False"),
            ("auth_type (in AUTHENTICATION_METHODS)", "session, jwt, token_auth, basic_auth, oauth, headers, custom")
        ]
        
        for setting, options in auth_types:
            auth_table.add_row(setting, options)
        
        self.console.print(auth_table)
        
        return self._show_continue_menu()
    
    def show_testing_frameworks_table(self):
        """Show comprehensive testing frameworks table"""
        self.clear_screen()
        
        # Testing frameworks table
        table = Table(title="🧪 Testing Framework Options", show_header=True, header_style="bold cyan")
        table.add_column("Config Setting", style="bold white", width=20)
        table.add_column("Available Options", style="green", width=50)
        
        testing_data = [
            ("TEST_FRAMEWORK", "pytest, unittest, nose2, robotframework, behave, tox, nox, testbook, hypothesis, great-expectations"),
            ("TEST_DIRECTORY", "tests, test, spec, src/tests, app/tests, . (current dir), or custom path"),
        ]
        
        for setting, options in testing_data:
            table.add_row(setting, options)
        
        self.console.print(table)
        self.console.print()
        
        # Testing tools table
        tools_table = Table(title="🛠️ Testing Library Config Options", show_header=True, header_style="bold green")
        tools_table.add_column("Config Setting", style="bold white", width=25)
        tools_table.add_column("Available Options", style="white", width=45)
        
        tools_data = [
            ("MOCK_LIBRARY", "pytest-mock, unittest.mock, doublex, flexmock, sure, none"),
            ("HTTP_MOCK_LIBRARY", "responses, httpretty, requests-mock, vcr, betamax, httmock, none"),
            ("FACTORY_LIBRARY", "factory_boy, faker, hypothesis, polyfactory, mimesis, mixer, model_bakery, fixtures, none"),
            ("COVERAGE_TOOL", "pytest-cov, coverage, none"),
            ("PARALLEL_TESTING", "pytest-xdist, pytest-parallel, none"),
            ("TEST_REPORTING", "pytest-html, allure-pytest, none"),
            ("PERFORMANCE_TESTING", "pytest-benchmark, locust, none")
        ]
        
        for setting, options in tools_data:
            tools_table.add_row(setting, options)
        
        self.console.print(tools_table)
        
        return self._show_continue_menu()
    
    def show_ml_frameworks_table(self):
        """Show ML/AI frameworks table"""
        self.clear_screen()
        
        table = Table(title="🤖 ML/AI Framework Config Options", show_header=True, header_style="bold cyan")
        table.add_column("Config Setting", style="bold white", width=25)
        table.add_column("Available Options", style="green", width=45)
        
        ml_data = [
            ("FRAMEWORK", "tensorflow, pytorch, scikit-learn, transformers, xgboost, lightgbm, jax, jupyter-ml, ml-project, generic"),
            ("MODEL_REGISTRY", "mlflow, wandb, neptune, none"),
            ("EXPERIMENT_TRACKING", "True, False"),
            ("MODEL_VERSIONING", "True, False"),
            ("DATA_VERSIONING", "True, False"),
            ("NOTEBOOK_ANALYSIS", "True, False")
        ]
        
        for setting, options in ml_data:
            table.add_row(setting, options)
        
        self.console.print(table)
        self.console.print()
        
        # ML Testing config
        patterns_table = Table(title="🧠 ML Testing Config Options", show_header=True, header_style="bold green")
        patterns_table.add_column("Config Setting", style="bold white", width=25)
        patterns_table.add_column("Available Options", style="white", width=45)
        
        patterns_data = [
            ("TRACK_HYPERPARAMETERS", "True, False"),
            ("TRACK_METRICS", "True, False"),
            ("TRACK_ARTIFACTS", "True, False")
        ]
        
        for setting, options in patterns_data:
            patterns_table.add_row(setting, options)
        
        self.console.print(patterns_table)
        
        return self._show_continue_menu()
    
    def show_database_options_table(self):
        """Show database and ORM options"""
        self.clear_screen()
        
        # Database table
        table = Table(title="🗄️ Database Config Options", show_header=True, header_style="bold cyan")
        table.add_column("Config Setting", style="bold white", width=20)
        table.add_column("Available Options", style="green", width=50)
        
        db_data = [
            ("ORM", "django-orm, sqlalchemy, peewee, tortoise-orm, sqlmodel, mongoengine, beanie, none"),
            ("DATABASES", "postgresql, mysql, sqlite, mongodb, redis, none"),
            ("CACHE_SYSTEMS", "redis, memcached, none"),
            ("ASYNC_DATABASE_SUPPORT", "True, False")
        ]
        
        for setting, options in db_data:
            table.add_row(setting, options)
        
        self.console.print(table)
        self.console.print()
        
        # Email and Job config table
        other_table = Table(title="📧 Email & Job Queue Config Options", show_header=True, header_style="bold green")
        other_table.add_column("Config Setting", style="bold white", width=20)
        other_table.add_column("Available Options", style="white", width=50)
        
        other_data = [
            ("EMAIL_BACKEND", "django-email, flask-mail, fastapi-mail, sendgrid, mailgun, postmark, aws-ses, smtplib, none"),
            ("JOB_QUEUE", "celery, rq, dramatiq, huey, apscheduler, django-q, arq, taskiq, none")
        ]
        
        for setting, options in other_data:
            other_table.add_row(setting, options)
        
        self.console.print(other_table)
        
        return self._show_continue_menu()
    
    def show_email_job_options_table(self):
        """Show email and job queue options"""
        return self.show_database_options_table()  # Redirect to database table which now includes email/job options
    
    def show_auth_examples(self):
        """Show authentication configuration examples"""
        self.clear_screen()
        
        # Framework selection with back option
        frameworks = [
            "Django", 
            "Flask", 
            "FastAPI", 
            "Generic/Custom",
            f"{self.theme.Icons.BACK} Back to Options Menu"
        ]
        
        choice = questionary.select(
            "Select framework for authentication examples:",
            choices=frameworks,
            style=self.get_common_style()
        ).ask()
        
        if choice is None or "Back" in choice:
            return "back"
        
        self._show_auth_example_for_framework(choice.lower())
        
        return self._show_continue_menu()
    
    def _show_auth_example_for_framework(self, framework):
        """Show authentication example for specific framework"""
        examples = {
            "django": {
                "title": "🔐 Django Authentication Examples",
                "config": '''# Django Authentication Configuration
AUTHENTICATION_METHODS = [
    {
        "method": "login_required",
        "file_location": "django.contrib.auth.decorators",
        "auth_type": "session"
    },
    {
        "method": "permission_required",
        "file_location": "django.contrib.auth.decorators",
        "auth_type": "session"
    },
    {
        "method": "user_passes_test",
        "file_location": "django.contrib.auth.decorators", 
        "auth_type": "session"
    }
]''',
                "usage": '''# Usage in Django views:
from django.contrib.auth.decorators import login_required, permission_required

@login_required
def my_view(request):
    # Only authenticated users can access
    pass

@permission_required('app.change_model')
def admin_view(request):
    # Only users with specific permission
    pass'''
            },
            "flask": {
                "title": "🔐 Flask Authentication Examples", 
                "config": '''# Flask Authentication Configuration
AUTHENTICATION_METHODS = [
    {
        "method": "login_required",
        "file_location": "flask_login",
        "auth_type": "session"
    },
    {
        "method": "jwt_required",
        "file_location": "flask_jwt_extended",
        "auth_type": "jwt"
    },
    {
        "method": "fresh_jwt_required",
        "file_location": "flask_jwt_extended",
        "auth_type": "jwt"
    }
]''',
                "usage": '''# Usage in Flask routes:
from flask_login import login_required
from flask_jwt_extended import jwt_required

@app.route('/protected')
@login_required
def protected():
    # Session-based auth
    pass

@app.route('/api/data')
@jwt_required()
def api_data():
    # JWT-based auth
    pass'''
            },
            "fastapi": {
                "title": "🔐 FastAPI Authentication Examples",
                "config": '''# FastAPI Authentication Configuration  
AUTHENTICATION_METHODS = [
    {
        "method": "get_current_user",
        "file_location": "app/auth.py",
        "auth_type": "jwt"
    },
    {
        "method": "get_current_active_user", 
        "file_location": "app/auth.py",
        "auth_type": "jwt"
    },
    {
        "method": "verify_api_key",
        "file_location": "app/auth.py",
        "auth_type": "headers"
    }
]''',
                "usage": '''# Usage in FastAPI endpoints:
from fastapi import Depends
from app.auth import get_current_user, verify_api_key

@app.get("/protected")
async def protected_route(user = Depends(get_current_user)):
    # JWT-based auth
    pass

@app.get("/api/data")
async def api_data(api_key = Depends(verify_api_key)):
    # API key auth
    pass'''
            },
            "generic/custom": {
                "title": "🔐 Generic/Custom Authentication Examples",
                "config": '''# Custom Authentication Configuration
AUTHENTICATION_METHODS = [
    {
        "method": "authenticate_user",
        "file_location": "app/auth.py",
        "auth_type": "session"
    },
    {
        "method": "require_api_key",
        "file_location": "app/middleware.py", 
        "auth_type": "headers"
    },
    {
        "method": "verify_token",
        "file_location": "app/security.py",
        "auth_type": "jwt"
    }
]''',
                "usage": '''# Usage with custom decorators:
from app.auth import authenticate_user
from app.middleware import require_api_key

@authenticate_user
def protected_function():
    # Custom session auth
    pass

@require_api_key
def api_endpoint():
    # Custom API key auth
    pass'''
            }
        }
        
        example = examples.get(framework, examples["generic/custom"])
        
        # Show configuration panel
        config_panel = Panel(
            example["config"],
            title=example["title"],
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(config_panel)
        self.console.print()
        
        # Show usage panel
        usage_panel = Panel(
            example["usage"],
            title="💡 Usage Example",
            border_style="yellow",
            padding=(1, 2)
        )
        self.console.print(usage_panel)
        self.console.print()
    
    def _show_continue_menu(self):
        """Show continue/back menu"""
        self.console.print()
        
        options = [
            f"{self.theme.Icons.BACK} Back to Options Menu",
            f"{self.theme.Icons.EXIT} Back to Main Menu"
        ]
        
        choice = questionary.select(
            "What would you like to do next?",
            choices=options,
            style=self.get_common_style()
        ).ask()
        
        if choice and "Options Menu" in choice:
            return self.show_main_options_menu()
        else:
            return "back"
