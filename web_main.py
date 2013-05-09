from flask import Flask

app = Flask('rss-digest')

@app.route('/')
def home():
    return "Welcome"
