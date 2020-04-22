from pymongo import MongoClient
from config.config_reader import ConfigReader


class DatabaseConnect():
    def __init__(self):

        # Initialization ConfigReader class
        self.config_reader = ConfigReader()

        # read_config method call
        self.configuration = self.config_reader.read_config()

        # storing mongodb connection url in mongo_connection variable
        self.mongo_connection = self.configuration['MONGO_CONNECTION']

        # Call for Mongo db connection
        cluster = MongoClient(self.mongo_connection)

        # mentioned collection name, in our case its covid
        db = cluster['covid']
        collection = db['covid']
        self.collection = collection

    def update_user_data(self, user_id, user_details):
        query = {"_id": user_id}
        new_values = {"$set": {"user_details": user_details}}

        cursor = self.collection.update(query, new_values)

    def add_user(self, user_id, user_details):
        user_dict = {"_id": user_id, "user_details": user_details}
        self.collection.insert_one(user_dict)

    def check_existing_user(self, user_id):
        result = self.collection.find_one({"_id": user_id})
        return result
