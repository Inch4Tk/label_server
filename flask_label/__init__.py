import os

from flask import Flask

def create_app(app_config=None):
    """App-factory function, which initializes our flask application."""
    environment = os.getenv('FLASK_ENV', 'production')

    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if environment == "development" and app_config is None:
        from . import config
        app_config = config.Dev(app.instance_path)
        app.logger.warning("THIS APP IS IN DEBUG MODE. YOU SHOULD NOT SEE THIS IN PRODUCTION.")

    app.config.from_object(app_config)  # Object base configuration

    if app_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)  # instance-folders configuration

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Prepare Database
    from .database import db, migrate, ma
    db.app = app
    db.init_app(app)
    migrate.init_app(app, db=db)
    ma.init_app(app)

    from flask_label.database_cli import init_db_cli
    init_db_cli(app)

    # Register Blueprints
    from . import auth
    app.register_blueprint(auth.bp)
    from . import api
    app.register_blueprint(api.bp)

    from . import index
    app.register_blueprint(index.bp)
    app.add_url_rule("/", endpoint="index.index")

    return app
