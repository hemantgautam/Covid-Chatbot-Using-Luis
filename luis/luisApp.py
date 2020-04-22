from botbuilder.core import TurnContext, ActivityHandler
from botbuilder.ai.luis import LuisApplication, LuisPredictionOptions, LuisRecognizer
from covid.covidApp import CovidInformation
from config.config_reader import ConfigReader
from logger.logger import Log
from mongo.mongo_connection import DatabaseConnect
import time
from covid_email.send_email import SendEmail
from flask import session


class LuisConnect(ActivityHandler):
    # Creating variables
    greet_text = "Hello, Welcome to Covid19 ChatBot. We will help you with precautions and current numbers of Corona infected"
    demographic_data_text = "Enter 'Country Name or Country Code or State Code'.To see demographically covid cases open this link https://covid19-flask-lui.herokuapp.com/demographic-covid-data"

    # fallback message, when bot couldnt find the specific result
    fall_back_msg = "Couldn't understand the county/state/code, please retype."
    data_process_msg = "Please wait for few seconds, we are processing your data."
    thanks_msg = "Thanks. We have sent necessary details in your email."

    # custom intent questions for bot
    bot_questions = {
        'start_text': 'Start Text',
        'name': "Enter Your Name",
        "email": "Enter your Email ID",
        "mobile": "Enter your Mobile Number",
        "pincode": "Enter your Pin Code",
    }

    def __init__(self):

        # initializating all the required classes
        self.collection = DatabaseConnect()
        self.covid_data = SendEmail()
        self.covid_info = CovidInformation()
        self.config_reader = ConfigReader()
        self.configuration = self.config_reader.read_config()
        # storing luis app credentials into varibales
        self.luis_app_id = self.configuration['LUIS_APP_ID']
        self.luis_endpoint_key = self.configuration['LUIS_ENDPOINT_KEY']
        self.luis_endpoint = self.configuration['LUIS_ENDPOINT']
        self.luis_app = LuisApplication(
            self.luis_app_id, self.luis_endpoint_key, self.luis_endpoint)
        self.luis_options = LuisPredictionOptions(
            include_all_intents=True, include_instance_data=True)
        self.luis_recognizer = LuisRecognizer(
            application=self.luis_app, prediction_options=self.luis_options, include_api_results=True)
        self.log = Log()

    '''
        This is the most important function, as this gets called 
        everytime any message activity heppens in chatbot
    '''
    async def on_message_activity(self, turn_context: TurnContext):
        luis_result = await self.luis_recognizer.recognize(turn_context)
        result = luis_result.properties["luisResult"]
        user_entered_message = str(result.query)

        # Storing users id to store data based on userid
        user_id = session.get('user_id')
        user_details_obj_len = 0
        is_user_exist = self.collection.check_existing_user(user_id)
        self.user_details = {}
        '''
        - Complete logic to show question to user is written here
        - User data stores in every message exchange
        - After collecting all the detail, email gets triggerd
        - If user enters any country code or name, it evaluates from here
        '''
        if is_user_exist is None:
            self.collection.add_user(user_id, '')
            is_user_exist = self.collection.check_existing_user(user_id)
            user_details_obj_len = 0
            user_id = is_user_exist['_id']
        else:
            user_id = is_user_exist['_id']
            user_details_obj_len = len(is_user_exist['user_details'])
            self.user_details = is_user_exist['user_details']
        if user_details_obj_len == 0:
            await turn_context.send_activity(self.greet_text)
            bot_ques_key = list(self.bot_questions.keys())[
                user_details_obj_len]
            self.user_details[bot_ques_key] = user_entered_message
            self.collection.update_user_data(
                user_id, self.user_details)
            bot_ques_value = list(self.bot_questions.values())[1]
            time.sleep(1)
            await turn_context.send_activity(bot_ques_value)
        else:
            print("DB User Obj len : " + str(user_details_obj_len) +
                  "---" + "Bot Question Number: " + str(len(self.bot_questions)))
            if user_details_obj_len == len(self.bot_questions):
                if user_entered_message.upper() == "Y":
                    covid_world_data = self.covid_info.get_world_covid_data()
                    await turn_context.send_activity(f"{covid_world_data}")
                    time.sleep(1)
                    await turn_context.send_activity(self.demographic_data_text)
                else:
                    try:
                        self.covid_info = CovidInformation()
                        covid_data = self.covid_info.get_covid_data_by_country(
                            user_entered_message)
                        await turn_context.send_activity(f"{covid_data}")
                        time.sleep(1)
                        await turn_context.send_activity(self.demographic_data_text)

                    except:
                        await turn_context.send_activity(
                            self.fall_back_msg)
            elif user_details_obj_len == len(self.bot_questions)-1:
                await turn_context.send_activity(self.data_process_msg)
                self.covid_data.send_covid_data(
                    is_user_exist['user_details']['email'])
                bot_ques_key = list(self.bot_questions.keys())[
                    user_details_obj_len]
                self.user_details[bot_ques_key] = user_entered_message
                self.collection.update_user_data(
                    user_id, self.user_details)
                await turn_context.send_activity(self.thanks_msg)
                time.sleep(1)
                await turn_context.send_activity(self.demographic_data_text)
            elif user_details_obj_len < len(self.bot_questions)-1:
                bot_ques_key = list(self.bot_questions.keys())[
                    user_details_obj_len]
                self.user_details[bot_ques_key] = user_entered_message
                self.collection.update_user_data(
                    user_id, self.user_details)
                await turn_context.send_activity(list(self.bot_questions.values())[user_details_obj_len+1])

    async def on_members_added_activity(self, members_added: "", turn_context: TurnContext):
        pass
