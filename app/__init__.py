from flask import Flask
from app.config import Config

def create_app():
    # Configura o Flask para buscar templates e estáticos dentro da pasta views
    app = Flask(__name__, 
                template_folder='views/templates', 
                static_folder='views/static')
    
    app.config.from_object(Config)

    from app.views.routes import main_bp
    app.register_blueprint(main_bp)

    return app