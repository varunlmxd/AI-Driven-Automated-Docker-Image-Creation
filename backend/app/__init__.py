from flask import Flask
from flask_cors import CORS
def create_app(config_name):
    """
    Create and configure the Flask application.

    Args:
        config_name (str): The configuration name to use for the Flask application.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)
    CORS(app)  # Enable Cross-Origin Resource Sharing (CORS) for the app
    
    # Load configuration from the specified config object
    app.config.from_object(f'config.{config_name.capitalize()}Config')

    # Import and register blueprints
    from .routes.build_and_run import build_and_run_bp
    from .routes.logs import logs_bp
    app.register_blueprint(build_and_run_bp)
    app.register_blueprint(logs_bp)
    
    return app