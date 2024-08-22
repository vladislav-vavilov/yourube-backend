from os import getenv

BASE_URL = 'https://www.youtube.com'

context = {
    'client': {
        'clientName': 'WEB',
        'clientVersion': '2.2024081',
    },
}

PROXY_HOST = '161.0.21.226'
PROXY_PORT = '8000'
PROXY_USERNAME = getenv('PROXY_USERNAME')
PROXY_PASSWORD = getenv('PROXY_PASSWORD')
