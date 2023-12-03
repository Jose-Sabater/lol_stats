from dotenv import dotenv_values


class Config:
    def __init__(self):
        self.config = dotenv_values(".env")

    def get(self, key):
        return self.config[key]
