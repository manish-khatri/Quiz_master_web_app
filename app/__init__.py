from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash
from datetime import date
from .models import db, Users
from .api import init_api

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///app.sqlite3'
    app.secret_key = '123'
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'static', 'images')

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    init_api(app)

    with app.app_context():
        db.create_all()

        admin = Users.query.filter_by(user_type='admin').first()
        if not admin:
            admin=Users(user_id='A0', user_mail='admin', user_name='admin', user_type='admin', user_pass=generate_password_hash('admin'),qualification='admin',dob=date(2000,1,1))
            db.session.add(admin)
            db.session.commit()

    return app
