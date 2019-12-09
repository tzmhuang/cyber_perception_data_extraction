import yaml

class ConfigParser(object):
    def __init__(self):
        return

    def load(self, config_file):
        with open(config_file, 'r') as f:
            self.config = yaml.load(f)
        return self.config
