import json
import os

class Config:
    def __init__(self, path):
        self.path = path
        self.data = {}
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.data = json.load(f)

        if not path.endswith('.json'):
            self.data['type_db'] = 'sqlite'


    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def set_type_db(self, type: str):
        self.data['type_db'] = type
        self.save()

    def get_type_db(self):
        return self.data['type_db']

    def set_type_db(self, type: str):
        self.data['type_db'] = type
        self.save()

    def get_connection(self):
        return self.data['connection']['host'], self.data['connection']['user'], self.data['connection']['password'], self.data['connection']['database']

    def set_connection(self, connection: str, host, user, password, database):
        self.data['connection']['host'] = host
        self.data['connection']['user'] = user
        self.data['connection']['password'] = password
        self.data['connection']['database'] = database
        self.save()

    # def set_connection(self, connection: str):