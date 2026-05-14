import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-padrao-de-desenvolvimento'
    # Você pode adicionar caminhos de banco de dados ou chaves de API aqui futuramente
    DEBUG = True
    DAGSTER_HOST = os.environ.get('DAGSTER_HOST') or 'localhost'
    DAGSTER_PORT = os.environ.get('DAGSTER_PORT') or '3000'