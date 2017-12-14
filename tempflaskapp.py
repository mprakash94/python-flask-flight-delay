from flask import Flask, render_template, request
import requests
import urllib
import urllib.request
import json
import requests
import os
import zipfile
from urllib.request import urlopen
from bs4 import BeautifulSoup
from zipfile import ZipFile
from io import BytesIO
import shutil
import pandas as pd
import urllib.request
from lxml import html
import gzip
import io
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import csv
import datetime

app = Flask(__name__)

@app.route('/result', methods=['POST'])
def result():
	year = request.form['year']
	day = request.form['day']
	month = request.form['month']
	deploc = request.form['oair']
	arrloc = request.form['dair']
	carrier = request.form['airlines']
	arrtimehr = request.form['arrhr']
	arrtimemin = request.form['arrmin']
	deptimehr = request.form['dephour']
	deptimemin = request.form['depmin']
	#To get the weather data based on year day and month and location
	url = "http://www.wunderground.com/history/airport/"+deploc+"/"+year+"/"+month+"/"+day+"/DailyHistory.html"
	page = urllib.request.urlopen(url)
	soup = BeautifulSoup(page,"lxml")
	table = soup.find("table", { "id" : "historyTable"})
	column_headers = ['event','actual','avg','record']
	player_data_02 = []  # create an empty list to hold all the data
	data_rows = table.findAll('tr')
	for i in range(len(data_rows)):  # for each table row
	    player_row = []  # create an empty list for each pick/player

	    # for each table data element from each table row
	    for td in data_rows[i].findAll('td'):

	        # get the text content and append to the row 
	        td_text=td.get_text().replace("\n","")
	        td_text_t = td_text.replace("\xa0","")
	        td_text_two=td_text_t.replace("\t","")
	        player_row.append(td_text_two)        

	    # then append each 
	    player_data_02.append(player_row)
	df = pd.DataFrame(player_data_02,columns=column_headers)
	df_temp = df.loc[df['event'] == 'Precipitation']
	df_temp = df_temp[(df_temp.actual != 'None')]
	df_temp = df_temp[(df_temp.avg != 'None')]
	df_temp = df_temp[(df_temp.record != 'None')]
	df_temp = df_temp.iloc[1:]
	precipitation =df_temp.actual.values
	if len(precipitation)==0:
	    precipe = '0'
	else:
		for i in precipitation:
		    precipe = i
		precipe = precipe.replace("in", "")
		if(precipe == ''):
		    precipe = '0'
		precipe = float(precipe)
		precipe=int(precipe)
		precipe = str(precipe)
	df_temp = df.loc[df['event'] == 'Wind Speed']
	winds =df_temp.actual.values
	if len(winds)==0:
	    wind = '0'
	else:
	    for i in winds:
	        wind = i
	    wind = wind.replace("mph ()", "")
	    wind = wind.replace("mph (WNW)", "")
	    wind = wind.replace("mph (South)", "")
	    if(wind == ''):
	        wind = '0'
	    wind = str(int(float(wind)))

	df_t = df.loc[df['event'] == 'Visibility']
	visibility =df_t.actual.values
	if len(visibility)==0:
	    visib = '0'
	else:
	    for i in visibility:
	        visib = i
	    visib = visib.replace("miles", "")
	    if(visib == ''):
	        visib = '0'

	departurehr = request.form['dephour']
	departuremin = request.form['depmin']
	departure = departurehr+':'+departuremin
	deptime = datetime.datetime.strptime(departure, '%H:%M').time()

	arrivalhr = request.form['arrhr']
	arrivalmin = request.form['arrmin']
	arrival = arrivalhr+':'+arrivalmin
	arrtime = datetime.datetime.strptime(arrival, '%H:%M').time()

	elapsetime = ((datetime.datetime.combine(datetime.date.today(), arrtime) - datetime.datetime.combine(datetime.date.today(), deptime)).total_seconds())/60 
	crselaptime = int(elapsetime)
	crselaptime = str(crselaptime)
	data = {
	        "Inputs": {
	                "input1":
	                [
	                    {
								'Year': year,   
								'Day': day,   
								'Month': month,   
								'Week': "7",   
								'Origin': deploc,   
								'Dest': arrloc,   
								'UniqueCarrier': carrier,   
								'CRSElapsedTime': crselaptime,   
								'OriginCityName': "Dallas/Fort Worth, TX",   
								'DestCityName': "Detroit, MI",   
								'Flight_Status': "1",   
								'OriginVisibility': visib,   
								'OriginWind': wind,
								'OriginPrecip': precipe,     
								'CRSDep_hour': deptimehr,   
								'CRSDep_min': deptimemin,   
								'CRSArr_hour': arrtimehr,   
								'CRSArr_min': arrtimemin,   
 
	                    }
	                ],
	        },
	    "GlobalParameters":  {
	    }
	}

	body = str.encode(json.dumps(data))

	url = 'https://ussouthcentral.services.azureml.net/workspaces/c2f8dc5126ac4024b08690eda8426a56/services/13fad7f731084ecca4ddeddadea11e3f/execute?api-version=2.0&format=swagger'
	api_key = 'YMDFoMKaifU5OfcWs8+0AXEgCYc2weCCpOmRiKiWr900cuZtO1KdJydq5LpocbQSoR8Y7IY1Lc6m4WPwDIqDSQ==' # Replace this with the API key for the web service
	headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

	req = urllib.request.Request(url, body, headers)

	try:
	    response = urllib.request.urlopen(req)

	    result = response.read()
	except urllib.error.HTTPError as error:
		result = "error"
	result = json.loads(result.decode("utf-8"))
	status = result['Results']['output1'][0]['CRSArr_min']

	#json_object = response.json
	#r = json_object['output1']['ArrDelayMinutes']
	return render_template('home.html',delaytime = status)

@app.route('/')
def index():
	calculations = ['Dallas/Fort Worth, TX', 'Detroit, MI', 'Seattle, WA',
       'New York, NY', 'San Jose, CA', 'Chicago, IL', 'Phoenix, AZ',
       'St. Louis, MO', 'Los Angeles, CA', 'Orlando, FL', 'Denver, CO',
       'Miami, FL', 'Houston, TX', 'Salt Lake City, UT', 'Tucson, AZ',
       'Boston, MA', 'Fort Lauderdale, FL', 'San Francisco, CA',
       'Kahului, HI', 'Tampa, FL', 'Santa Ana, CA', 'Oklahoma City, OK',
       'Honolulu, HI', 'Philadelphia, PA', 'Raleigh/Durham, NC',
       'Washington, DC', 'Richmond, VA', 'Atlanta, GA', 'Lubbock, TX',
       'Charlotte, NC', 'El Paso, TX', 'Nashville, TN', 'Jackson, WY',
       'Sacramento, CA', 'Newark, NJ', 'Lihue, HI', 'San Juan, PR',
       'Albuquerque, NM', 'Norfolk, VA', 'Jacksonville, FL',
       'New Orleans, LA', 'Kansas City, MO', 'Gunnison, CO',
       'Indianapolis, IN', 'Portland, OR', 'Baltimore, MD',
       'Minneapolis, MN', 'Milwaukee, WI', 'Ontario, CA', 'Fort Myers, FL',
       'Des Moines, IA', 'Palm Springs, CA', 'Eagle, CO',
       'West Palm Beach/Palm Beach, FL', 'Louisville, KY',
       'Pittsburgh, PA', 'Dayton, OH', 'Christiansted, VI',
       'Colorado Springs, CO', 'Columbus, OH', 'Montrose/Delta, CO',
       'Hayden, CO', 'Hartford, CT', 'Memphis, TN', 'Cleveland, OH',
       'Oakland, CA', 'Spokane, WA', 'Anchorage, AK', 'Buffalo, NY',
       'Syracuse, NY', 'Albany, NY', 'Providence, RI', 'Wilmington, NC',
       'Wichita, KS', 'Portland, ME', 'Greensboro/High Point, NC',
       'Charleston, SC', 'Harrisburg, PA', 'Birmingham, AL', 'Kodiak, AK',
       'Barrow, AK', 'Deadhorse, AK', 'Juneau, AK', 'Ketchikan, AK',
       'Yakutat, AK', 'Cordova, AK', 'Petersburg, AK', 'Wrangell, AK',
       'Nome, AK', 'Kotzebue, AK', 'Burbank, CA', 'Adak Island, AK',
       'Newburgh/Poughkeepsie, NY', 'Long Beach, CA', 'Ponce, PR',
       'Aguadilla, PR', 'White Plains, NY', 'Savannah, GA',
       'Sarasota/Bradenton, FL', 'Burlington, VT', 'Worcester, MA',
       'Cincinnati, OH', 'Bismarck/Mandan, ND', 'Asheville, NC',
       'Grand Rapids, MI', 'Flint, MI', 'Myrtle Beach, SC',
       'Jackson/Vicksburg, MS', 'Fargo, ND', 'Pensacola, FL',
       'Augusta, GA', 'Lexington, KY', 'Dallas, TX', 'Appleton, WI',
       'Gulfport/Biloxi, MS', 'Melbourne, FL', 'Bozeman, MT',
       'Charlottesville, VA', 'Madison, WI', 'Key West, FL',
       'Bristol/Johnson City/Kingsport, TN', 'Lafayette, LA',
       'Roanoke, VA', 'Panama City, FL', 'Valparaiso, FL',
       'Fayetteville, AR', 'Evansville, IN', 'Scranton/Wilkes-Barre, PA',
       'Huntsville, AL', 'Fayetteville, NC', 'Knoxville, TN',
       'Tallahassee, FL', 'Missoula, MT', 'Trenton, NJ',
       'Newport News/Williamsburg, VA', 'Sioux Falls, SD', 'Latrobe, PA',
       'Bloomington/Normal, IL', 'Charleston/Dunbar, WV', 'Pago Pago, TT',
       'Niagara Falls, NY', 'Waco, TX', 'Shreveport, LA', 'Fort Smith, AR',
       'Midland/Odessa, TX', 'Santa Fe, NM', 'Joplin, MO', 'Laredo, TX',
       'Brownsville, TX', 'Tyler, TX', 'Grand Junction, CO', 'Duluth, MN',
       'Santa Barbara, CA', 'Aspen, CO', 'Idaho Falls, ID',
       'Rapid City, SD', 'Kalispell, MT', 'Lincoln, NE', 'Amarillo, TX',
       'Bakersfield, CA', 'Moline, IL', 'La Crosse, WI', 'South Bend, IN',
       'Pasco/Kennewick/Richland, WA', 'Flagstaff, AZ', 'Williston, ND',
       'Grand Forks, ND', 'Great Falls, MT', 'Monterey, CA',
       'Saginaw/Bay City/Midland, MI', 'Sun Valley/Hailey/Ketchum, ID',
       'Twin Falls, ID', 'Springfield, MO', 'Casper, WY',
       'Baton Rouge, LA', 'Plattsburgh, NY', 'Corpus Christi, TX',
       'Cedar Rapids/Iowa City, IA', 'San Luis Obispo, CA',
       'Rock Springs, WY', 'Hancock/Houghton, MI', 'Mammoth Lakes, CA',
       'Pellston, MI', 'Elko, NV', 'Gillette, WY', 'Medford, OR',
       'Santa Maria, CA', 'Eugene, OR', 'Rochester, MN',
       'Traverse City, MI', 'Springfield, IL', 'St. George, UT',
       'Helena, MT', 'Bend/Redmond, OR', 'Arcata/Eureka, CA',
       'Eau Claire, WI', 'Devils Lake, ND', 'Jamestown, ND',
       'Muskegon, MI', 'Hays, KS', 'Cody, WY', 'Ithaca/Cortland, NY',
       'Alpena, MI', 'Escanaba, MI', 'Bemidji, MN', 'Marquette, MI',
       'Binghamton, NY', 'Rhinelander, WI', 'Lewiston, ID',
       'Iron Mountain/Kingsfd, MI', 'Brainerd, MN',
       'International Falls, MN', 'Pocatello, ID', 'Guam, TT',
       'Hibbing, MN', 'Butte, MT', 'Cedar City, UT',
       'North Bend/Coos Bay, OR', 'Redding, CA',
       'Harlingen/San Benito, TX', 'Islip, NY', 'Manchester, NH',
       'Gainesville, FL', 'Meridian, MS', 'Hattiesburg/Laurel, MS',
       'Beaumont/Port Arthur, TX', 'Alexandria, LA', 'Texarkana, AR',
       'Roswell, NM', 'College Station/Bryan, TX', 'Hobbs, NM',
       'Lake Charles, LA', 'Jacksonville/Camp Lejeune, NC',
       'Elmira/Corning, NY', 'Valdosta, GA', 'Montgomery, AL',
       'Bangor, ME', 'Columbus, MS', 'Columbus, GA', 'Brunswick, GA',
       'Dothan, AL', 'New Bern/Morehead/Beaufort, NC', 'Albany, GA',
       'Wichita Falls, TX', 'San Angelo, TX', 'Longview, TX',
       'Nantucket, MA', "Martha's Vineyard, MA", 'Hyannis, MA',
       'Gustavus, AK', 'King Salmon, AK', 'Dillingham, AK',
       'Garden City, KS', 'Manhattan/Ft. Riley, KS', 'Abilene, TX',
       'Grand Island, NE', 'Punta Gorda, FL', 'Saipan, TT']

       
	return render_template('home.html', calculations=calculations)

if __name__ == '__main__':
	app.run(debug=True)