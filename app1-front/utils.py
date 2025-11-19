# -*- coding: utf-8 -*- 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
ALLOWED_VIDEO_EXTENSIONS = set(['mp4', 'avi', 'mov', 'mkv', 'webm'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_video(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS
