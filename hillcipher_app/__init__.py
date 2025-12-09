from flask import Flask
from database import init_database
from .routes import bp


def create_app():
    """Application factory."""
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )
    app.secret_key = "hill-cipher-secret-key-2024"

    # Initialize database and register blueprints
    init_database()
    app.register_blueprint(bp)

    return app

