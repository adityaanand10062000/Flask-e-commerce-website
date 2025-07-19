# app/__init__.py
from flask import Flask, session
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'
    bcrypt.init_app(app)

    # We have removed all the Flask-Admin code

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    from app.models import User, Product

    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'User': User, 'Product': Product}

    @app.context_processor
    def inject_cart():
        cart = session.get('cart', {})
        total_quantity = sum(item['quantity'] for item in cart.values())
        return dict(cart=cart, cart_total_quantity=total_quantity)

    return app
