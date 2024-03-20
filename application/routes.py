from flask import current_app as app
from flask import render_template

from .clients import openai_client

@app.route("/")
def home_page():
    return render_template("index.html")