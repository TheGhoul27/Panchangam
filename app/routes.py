from flask import render_template, current_app as app
from .scraper import get_panchangam


@app.route('/')
def index():
    panchangam_data = get_panchangam()
    return render_template('index.html', panchangam=panchangam_data)
