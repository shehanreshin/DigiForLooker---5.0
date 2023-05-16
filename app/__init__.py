from flask import Flask
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'blahblahblah' #change this key later
app.config['UPLOAD_FOLDER'] = 'static/files/uploaded'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_COOKIE_EXPIRES'] = datetime.now() - timedelta(days=1)

from app import views