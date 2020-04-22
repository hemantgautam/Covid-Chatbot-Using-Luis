from config_reader import ConfigReader
import requests
import pandas as pd


class CovidInformation():
    def __init__(self):

        # Initialization ConfigReader to readcovid apis host and key
        self.config_reader = ConfigReader()
        self.configuration = self.config_reader.read_config()
        self.x_rapidapi_host = self.configuration['X_RAPIDAPI_HOST']
        self.x_rapidapi_key = self.configuration['X_RAPIDAPI_KEY']

    def get_world_covid_data(self):
        '''
            Try catch is important here to use two different apis,
            incase one api is down so other api should return the data 
        '''
        try:
            url = "https://covid-19-data.p.rapidapi.com/totals"
            querystring = {"format": "json"}

            # header information
            headers = {
                'x-rpidapi-host': self.x_rapidapi_host,
                'x-rapidapi-key': self.x_rapidapi_key
            }

            # passing url, header and querystring which return the data
            covid_world_data = requests.request(
                "GET", url, headers=headers, params=querystring)

            # convert repsone into json
            covid_world_data = covid_world_data.json()

            # store in variables
            confirmed = covid_world_data[0]['confirmed']
            recovered = covid_world_data[0]['recovered']
            critical = covid_world_data[0]['critical']
            deaths = covid_world_data[0]['deaths']

            # Return the repsonse to user in chat
            self.bot_says = f"Total Confirmed cases across world: Confirmed: {confirmed}, Recovered: {recovered}, Critical: {critical}, Deaths: {deaths}"
            return self.bot_says

        except:

            # direct call to url which return json respone
            r = requests.get(
                'https://coronavirus-tracker-api.herokuapp.com/v2/locations')

            # read return data as json
            load_json_data = r.json()

            # creating Dataframe of response using pandas
            covid_df = pd.DataFrame(load_json_data['locations'])

            # Setting country as index
            covid_df.set_index('country', inplace=True)

            # taking latest data out of dataframe
            covid_data = load_json_data['latest']

            # Returing world wide data
            self.bot_says = f"Total Confirmed cases across world: {covid_data['confirmed']}, Total Deaths: {covid_data['deaths']}"
            return self.bot_says

    def get_covid_data_by_country(self, country):
        '''
        As we are asking user to add country code or state code,
        this wil be always in lenth of two, that is getting checked here
        '''
        if len(country) == 2:

            # First we are checking indian state
            url = "https://covid19india.p.rapidapi.com/getStateData/"+country

            # header information
            headers = {
                'x-rapidapi-host': "covid19india.p.rapidapi.com",
                'x-rapidapi-key': self.x_rapidapi_key
            }

            # passing url, header and querystring which return the data
            covid_world_data = requests.request("GET", url, headers=headers)

            # convert repsone into json
            covid_world_data = covid_world_data.json()

            # if this api return status as success, it returns result
            if covid_world_data['status'] == "Success":

                # Returing indian state data
                self.bot_says = f"Total Confirmed cases in {covid_world_data['response']['name']}: {covid_world_data['response']['confirmed']}, Total Deaths: {covid_world_data['response']['deaths']}, Total Recovered: {covid_world_data['response']['recovered']}"
                return self.bot_says
            else:

                # this block of code runs when user enter country code
                url = "https://covid-19-data.p.rapidapi.com/country/code"
                headers = {
                    'x-rapidapi-host': self.x_rapidapi_host,
                    'x-rapidapi-key': self.x_rapidapi_key
                }
                querystring = {"format": "json", "code": country}
                covid_world_data = requests.request(
                    "GET", url, headers=headers, params=querystring)

                # convert repsone into json
                covid_world_data = covid_world_data.json()

                # store in variables
                country = covid_world_data[0]['country']
                confirmed = covid_world_data[0]['confirmed']
                recovered = covid_world_data[0]['recovered']
                deaths = covid_world_data[0]['deaths']
                critical = covid_world_data[0]['critical']

                # Returing country data by country code
                self.bot_says = f"Total Confirmed cases in {country}: {confirmed}, Total Deaths: {deaths}, Total Recovered: {recovered}, Serious/Critical: {critical}"
                return self.bot_says
        else:

            # this block of code gets excuted when user enter country name
            url = "https://covid-19-data.p.rapidapi.com/country"
            querystring = {"format": "json", "name": country}

            # header information
            headers = {
                'x-rapidapi-host': self.x_rapidapi_host,
                'x-rapidapi-key': self.x_rapidapi_key
            }
            covid_world_data = requests.request(
                "GET", url, headers=headers, params=querystring)

            # convert repsone into json
            covid_world_data = covid_world_data.json()

            # store in variables
            country = covid_world_data[0]['country']
            confirmed = covid_world_data[0]['confirmed']
            recovered = covid_world_data[0]['recovered']
            deaths = covid_world_data[0]['deaths']
            critical = covid_world_data[0]['critical']

            # Returing country data by country Name
            self.bot_says = f"Total Confirmed cases in {country}: {confirmed}, Total Deaths: {deaths}, Total Recovered: {recovered}, Serious/Critical: {critical}"
            return self.bot_says
