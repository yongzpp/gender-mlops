import os

import yaml


def load_hparam(filename):
    stream = open(filename, 'r', encoding='utf-8')
    docs = yaml.load_all(stream, Loader=yaml.SafeLoader)
    hparam_dict = {}
    for doc in docs:
        for k, v in doc.items():
            hparam_dict[k] = v
    return hparam_dict


class Dotdict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dct=None):
        dct = {} if not dct else dct
        for key, value in dct.items():
            if hasattr(value, 'keys'):
                value = Dotdict(value)
            self[key] = value


class Config(Dotdict):
    def __init__(self):
        file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
        super(Dotdict, self).__init__()
        hp_dict = load_hparam(file)
        hp_dotdict = Dotdict(hp_dict)
        for k, v in hp_dotdict.items():
            setattr(self, k, v)

    __getattr__ = Dotdict.__getitem__
    __setattr__ = Dotdict.__setitem__
    __delattr__ = Dotdict.__delitem__


cfg = Config()
