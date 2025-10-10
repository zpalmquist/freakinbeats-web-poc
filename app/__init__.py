from flask import Flask
from flask_assets import Environment, Bundle
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Setup Flask-Assets
    assets = Environment(app)
    assets.url = app.static_url_path
    scss = Bundle('scss/main.scss', 'scss/cart.scss', 'scss/detail.scss', filters='libsass', output='css/all.css')
    assets.register('scss_all', scss)
    
    from app.routes import api, main
    app.register_blueprint(api.bp)
    app.register_blueprint(main.bp)
    
    return app
