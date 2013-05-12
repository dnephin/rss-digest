from flask import Flask

from rssdigest import config

app = Flask(config.app_name)

@app.route('/')
def home():
    return "Welcome"
