"""About UI screen"""

from rich.text import Text
from .base_ui import BaseUI

class AboutUI(BaseUI):
    def show(self):
        """Display about information screen"""
        self.clear_screen()
        
        # Create about content using theme
        about_text = Text()
        about_text.append("TNG Python\n", style=self.theme.TextStyles.TITLE)
        about_text.append("Version: 0.1.0\n\n", style=self.theme.Colors.TEXT_MUTED)
        about_text.append("LLM-powered test generation tool that automatically creates comprehensive tests for your Python applications.\n\n", style=self.theme.Colors.TEXT_PRIMARY)
        
        about_text.append("Command Line Usage:\n", style=self.theme.TextStyles.HEADER)
        about_text.append(f"{self.theme.Icons.BULLET} tng                          # Interactive mode\n", style=self.theme.Colors.TEXT_PRIMARY)
        about_text.append(f"{self.theme.Icons.BULLET} tng -f users.py -m save      # Generate test for specific method\n", style=self.theme.Colors.TEXT_PRIMARY)
        about_text.append(f"{self.theme.Icons.BULLET} tng init                     # Generate configuration file\n\n", style=self.theme.Colors.TEXT_PRIMARY)
        
        about_text.append("Supported Technologies:\n", style=self.theme.TextStyles.HEADER)
        about_text.append(f"{self.theme.Icons.BULLET} Web Frameworks: Django, Flask, FastAPI, Tornado, Pyramid, Bottle, Quart, Sanic, Starlette, CherryPy\n", style=self.theme.Colors.TEXT_PRIMARY)
        about_text.append(f"{self.theme.Icons.BULLET} ML/AI Frameworks: TensorFlow, PyTorch, Scikit-learn, Keras, XGBoost, LightGBM, Pandas, NumPy, Hugging Face, OpenAI\n", style=self.theme.Colors.TEXT_PRIMARY) 
        about_text.append(f"{self.theme.Icons.BULLET} Database/ORM: SQLAlchemy, Django ORM, Peewee, Tortoise ORM, SQLModel, MongoEngine, Beanie, Raw SQL\n", style=self.theme.Colors.TEXT_PRIMARY)
        about_text.append(f"{self.theme.Icons.BULLET} Testing Frameworks: pytest, unittest, nose2, testify, hypothesis, factory_boy, responses, httpx\n", style=self.theme.Colors.TEXT_PRIMARY)
        about_text.append(f"{self.theme.Icons.BULLET} Email Systems: Django Email, Flask-Mail, FastAPI-Mail, SendGrid, Mailgun, Postmark, AWS SES, SMTP\n", style=self.theme.Colors.TEXT_PRIMARY)
        about_text.append(f"{self.theme.Icons.BULLET} Background Jobs: Celery, RQ, Dramatiq, Huey, APScheduler, Django-Q, ARQ, TaskIQ\n\n", style=self.theme.Colors.TEXT_PRIMARY)
        
        about_text.append(f"{self.theme.Icons.LINK}  https://tng.sh\n", style=self.theme.Colors.INFO)
        about_text.append(f"{self.theme.Icons.EMAIL}  Support: support@tng.sh", style=self.theme.Colors.TEXT_MUTED)
        
        about_panel = self.create_centered_panel(
            about_text,
            title=self.theme.Titles.ABOUT,
            border_style=self.theme.Colors.BORDER_DEFAULT
        )
        
        self.console.print(about_panel)
        self.press_any_key()
