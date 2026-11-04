import os

from flask import Flask

from .routes import main


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("FLASK_SECRET_KEY", "dev-only-change-me"),
        MAX_CONTENT_LENGTH=int(os.getenv("MAX_CONTENT_LENGTH", 5 * 1024 * 1024)),
        JSON_SORT_KEYS=False,
    )
    if test_config:
        app.config.update(test_config)

    app.register_blueprint(main)
    return app
