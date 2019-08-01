import os

import yaml


class Experiment:
    '''experiment in fuga'''
    def __init__(
            self,
            name,
            root_path):
        self.name = name
        self.root_path = root_path

    @classmethod
    def from_path(cls, path):
        with open(os.path.join(path, 'fuga.yml')) as f:
            config = yaml.load(f)

        return cls(config['experiment_name'], path)
