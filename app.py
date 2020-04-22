from flask import Flask, request, Response, render_template, session
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity
import asyncio
from luis.luisApp import LuisConnect
import os
from logger.logger import Log
import requests
from flask_session import Session
from configure import DefaultConfig
from config.config_reader import ConfigReader

app = Flask(__name__)
app.config.update(SECRET_KEY=os.urandom(24))
loop = asyncio.get_event_loop()
CONFIG = DefaultConfig()

bot_settings = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
bot_adapter = BotFrameworkAdapter(bot_settings)
luis_bot_dialog = LuisConnect()

config_reader = ConfigReader()
configuration = config_reader.read_config()
x_rapidapi_host = configuration['X_RAPIDAPI_HOST']
x_rapidapi_key = configuration['X_RAPIDAPI_KEY']
user_session_id = ''
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = os.urandom(12).hex()
# PERMANENT_SESSION_LIFETIME = 1800
Session(app)


@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" in request.headers["content-type"]:
        log = Log()
        request_body = request.json

        session['user_id'] = request_body['from']['id']
        print("SESSION_ID:" + session['user_id'])
        user_says = Activity().deserialize(request_body)
        authorization_header = (
            request.headers["Authorization"] if "Authorization" in request.headers else "")

        async def call_user_fun(turncontext):
            await luis_bot_dialog.on_turn(turncontext)
        task = loop.create_task(
            bot_adapter.process_activity(
                user_says, authorization_header, call_user_fun)
        )
        loop.run_until_complete(task)
        return ""
    else:
        return Response(status=406)

# function to show demographic data in a seperate Url
@app.route('/demographic-covid-data', methods=['GET'])
def demographic_covid_data():
    url = "https://covid-19-data.p.rapidapi.com/country/all"
    querystring = {"format": "json"}
    headers = {
        'x-rapidapi-host': x_rapidapi_host,
        'x-rapidapi-key': x_rapidapi_key
    }
    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    covid_world_data = response.json()
    return render_template('covid_demographic_data.html', covid_world_data=covid_world_data)


if __name__ == '__main__':
    app.run()
