import os


def get_env_or_raise(name, default_value=None):
    var = os.environ.get(name)
    msg = '{} is not set in environment variables'
    if not var and default_value is None:
        raise ValueError(msg.format(name))
    if not var and default_value is not None:
        return default_value
    return var

BD_URI = get_env_or_raise('DB_URI')
