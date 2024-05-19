from bs4 import BeautifulSoup as bs
import requests as req
import datetime


def get_content(url, css):
    page = req.get(url)
    soup = bs(page.content, "html.parser")
    panchangam = soup.select(css)
    return panchangam


def get_panchangam(date_obj):
    css = "td"
    date_str = date_obj.strftime('%Y-%m-%d')
    # url = "https://www.panchangam.org/global/daily.php?city=New+York#google_vignette"
    url = f"https://www.panchangam.org/global/daily.php?city=New+York&date={date_str}"

    day_map = {
        'Monday': 'Indu Vasara',
        'Tuesday': 'Bhauma Vasara',
        'Wednesday': 'Saumya Vasara',
        'Thursday': 'Guru Vasara',
        'Friday': 'Bhrigu Vasara',
        'Saturday': 'Sthira Vasara',
        'Sunday': 'Bhanu Vasara'
    }

    ruthu_map = {
        'Chaithra': 'Vasanta Ruthu',
        'Vaisakha': 'Vasanta Ruthu',
        'Jyeshta': 'Greeshma Ruthu',
        'Ashadha': 'Greeshma Ruthu',
        'Sravana': 'Greeshma Ruthu',
        'Bhadrapada': 'Greeshma Ruthu',
        'Ashvina': 'Sharada Ruthu',
        'Kartika': 'Sharada Ruthu',
        'Margashirsha': 'Hemanta Ruthu',
        'Pushya': 'Hemanta Ruthu',
        'Magha': 'Shishira Ruthu',
        'Phalguna': 'Shishira Ruthu'
    }

    ayana_map = {
        'Chaithra': 'Uttharayana',
        'Vaisakha': 'Uttharayana',
        'Jyeshta': 'Uttharayana',
        'Ashadha': 'Daakshinayana',
        'Sravana': 'Daakshinayana',
        'Bhadrapada': 'Daakshinayana',
        'Ashvina': 'Daakshinayana',
        'Kartika': 'Daakshinayana',
        'Margashirsha': 'Daakshinayana',
        'Pushya': 'Uttharayana',
        'Magha': 'Uttharayana',
        'Phalguna': 'Uttharayana'
    }

    content = get_content(url, css)

    all_vals = []
    for i in content:
        all_vals.append(i.text)

    today = datetime.date.today()
    weekday_number = today.weekday()
    weekday_name = datetime.date.today().strftime("%A")

    title = all_vals[0]

    col1 = ['Samvatsara']
    col2 = ['Krodhi Nama Samvatsara']

    skip = 0
    for i in range(1, len(all_vals)):
        if all_vals[i] in ['Panchangam', 'Time to Avoid (Bad time to start any important work)', 'Good Time (to start any important work)']:
            continue
        elif skip % 2 != 0:
            col2.append(all_vals[i])
            skip += 1
        else:
            col1.append(all_vals[i])
            skip += 1

    title = title.replace("Today's ", '')
    panchangam = {
        'Title': title,
    }

    for a, b in zip(col1, col2):
        temp = a.split(' ')
        if len(temp) > 1:
            a = '_'.join(temp)
        else:
            a = temp[0]
        if a == 'Month':
            if b == 'Agrahayana':
                b = 'Margashirsha'
            elif b == 'Pausa':
                b = 'Pushya'

            panchangam['Masa'] = b
            panchangam['Ayana'] = ayana_map[b]
            panchangam['Ruthu'] = ruthu_map[b]
            panchangam['Vasara'] = day_map[weekday_name]
        else:
            if a in ['Tithi', 'Nakshatram', 'Yogam', 'Karanam']:
                b = b.replace('  ', '\n')
            panchangam[a] = b

    details = f'City: {panchangam["City"]}, Sunrise: {panchangam["Sunrise"]}, Sunset: {panchangam["Sunset"]}'
    panchangam['Details'] = details
    panchangam.pop('City', None)
    panchangam.pop('Sunrise', None)
    panchangam.pop('Sunset', None)

    panchangam = {k.lower(): v for k, v in panchangam.items()}
    return panchangam
