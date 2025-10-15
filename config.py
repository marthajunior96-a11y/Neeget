import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key_that_should_be_changed_in_production'
    JSON_DATABASE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')


