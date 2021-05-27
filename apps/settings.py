import os


def get_env_or_raise(name, default_value=None):
    """Get environment settings"""
    var = os.environ.get(name)
    msg = '{} is not set in environment variables'
    if not var and default_value is None:
        raise ValueError(msg.format(name))
    if not var and default_value is not None:
        return default_value
    return var

DB_NAME = get_env_or_raise('DB_NAME')
DB_HOST = get_env_or_raise('DB_HOST')
DB_USER = get_env_or_raise('DB_USER')
DB_PASSWORD = get_env_or_raise('DB_PASSWORD')

DB_URI = "postgresql://{db_user}:{db_password}@{db_host}/{db_name}".format(
    db_user=DB_USER,
    db_password=DB_PASSWORD,
    db_host=DB_HOST,
    db_name=DB_NAME,
) 

VALID_USER = get_env_or_raise('VALID_USER')
VALID_PASSWORD = get_env_or_raise('VALID_PASSWORD')