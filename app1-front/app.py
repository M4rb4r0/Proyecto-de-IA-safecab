# -*- coding: utf-8 -*-
from flask import Flask
import os

IA_SERVER = os.environ.get('IA_SERVER', 'http://10.0.218.101:7060')

IA_URL = '/safecab/app1-ia/predict'
IA_VIDEO_URL = '/safecab/app1-ia/predict-video'

UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__,
            static_url_path='/safecab/app1-front/static')
            
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB para videos
