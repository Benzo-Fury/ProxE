import config

class Logger:
    def debug(self, l: str): 
        if config.debug:
            print(l)

    def info(self, l: str):
        print(l)

    def error(self, l: str):
        print(l)