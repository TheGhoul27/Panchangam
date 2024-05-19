from flask import render_template, request, current_app as app
from .scraper import get_panchangam
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
def index():
    cities = ['Atlanta, USA', 'Chicago, USA', 'Houston, USA', 'New Jersey, USA', 'New York, USA', 'Toronto, Ontario, Canada', 'London, UK', 'Edinburgh, UK', 'Sydney, Australia', 'Melbourne, Australia', 'Perth, Australia', 'Durban, South Africa',
              'Cape Town, South Africa', 'Munich, Germany', 'Singapore, Singapore', 'Kuala Lumpur, Malaysia', 'Dubai, UAE', 'Bangkok, Thailand', 'Hongkong, China', 'Riyadh, Saudi Arabia', 'Doha, Qatar', 'Kuwait City, Kuwait', 'Hamilton, New Zealand', 'Auckland, New Zealand']
    if request.method == 'POST':
        date_str = request.form['date']
        city = request.form['city']
        city = city.split(',')[0]
        city = city.replace(' ', '+')
        city = city.replace(' City', '')
        city = city.replace(' city', '')
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            date_obj = datetime.now()
    else:
        date_obj = datetime.now()
        city = 'New+York'
    panchangam_data = get_panchangam(date_obj, city)
    return render_template('index.html', panchangam=panchangam_data, date=date_obj.strftime('%Y-%m-%d'), cities=cities, selected_city=city)
