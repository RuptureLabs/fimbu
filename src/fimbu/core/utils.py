import configparser
import os


def load_init_settings() -> configparser.ConfigParser:
    """
    This is used the first time settings are needed, if the user hasn't
    configured settings manually.
    """
    config = configparser.ConfigParser()
    path = os.path.join(os.curdir, "fimbu.ini")

    if os.path.exists(path):
        config.read(path)
    else:
        config['default'] = {
            'settings': 'fimbu.conf.global_settings',
        }
    return config
