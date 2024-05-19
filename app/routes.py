from flask import render_template, request, current_app as app
from .scraper import get_panchangam
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        date_str = request.form['date']
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            date_obj = datetime.now()
    else:
        date_obj = datetime.now()
    panchangam_data = get_panchangam(date_obj)
    return render_template('index.html', panchangam=panchangam_data, date=date_obj.strftime('%Y-%m-%d'))
