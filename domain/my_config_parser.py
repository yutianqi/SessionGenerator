import configparser


class MyConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr
