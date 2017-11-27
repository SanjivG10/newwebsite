from flask import Flask,render_template as render , request
import feedparser
import json
import urllib2
import datetime
from flask import make_response

 
app= Flask(__name__)

EXCHANGE_RATE_API_KEY="71f063b0214745ad9fae3bb487b14aab"
WEATHER_API_KEY = "3d78a5edcbb22e3dcd18e6ec296c9016"
BBC_FEED="http://feeds.bbci.co.uk/news/rss.xml"
#just a random command

DEFAULTS = {'publication':'bbc',
'city': 'London,UK',
'currency_from':'GBP',
'currency_to' :'USD'
}





@app.route("/", methods =['GET','POST'])
def homepage():
	city = get_value_with_fallback('city')
	weather = get_weather_data(city)
	bbc_news_feed = feedparser.parse(BBC_FEED)
	currency_from = get_value_with_fallback("currency_from")

	currency_to = get_value_with_fallback("currency_to")

	rate,currencies = get_exchangerate_data(currency_from, currency_to)
	currencies = sorted(currencies)
	expires = datetime.datetime.now() + datetime.timedelta(days=365)
	response = make_response(render("homepage.html",
							articles=bbc_news_feed["entries"],
							weather=weather,
							currency_from=currency_from,
							currency_to=currency_to,
							rate=rate,
							currencies=sorted(currencies)))
	response.set_cookie("city", city, expires=expires)
	response.set_cookie("currency_from",
	currency_from, expires=expires)
	response.set_cookie("currency_to", currency_to, expires=expires)
	return response

def get_weather_data(query): 
	api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid="+WEATHER_API_KEY
	query = urllib2.quote(query)
	url= api_url.format(query)
	data = urllib2.urlopen(url).read()
	json_data = json.loads(data)
	return json_data

def get_exchangerate_data(frm_data,to_data):
	api_url="https://openexchangerates.org/api/latest.json?app_id="+EXCHANGE_RATE_API_KEY	
	data = urllib2.urlopen(api_url).read()
	parsed_data = json.loads(data).get("rates")
	from_rate = (parsed_data.get(frm_data.upper()))
	to_rate = (parsed_data.get(to_data.upper()))
	return (to_rate/from_rate,parsed_data.keys())

def get_value_with_fallback(key):
	if request.args.get(key):
		return request.args.get(key)
	if request.form.get(key):
		return request.form.get(key)	
	if request.cookies.get(key):
		return request.cookies.get(key)
	return DEFAULTS[key]



if __name__== "__main__":
	app.run(debug=True)	