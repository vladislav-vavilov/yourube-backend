import requests
from parsers.common import random_proxy


def get_image(path: str) -> requests.Response:
    image_type = path.split('/')[0]
    base_url = get_base_url(image_type)

    url = f'https://{base_url}/{path}'
    response = requests.get(url=url, proxies=random_proxy, stream=True)

    return response


def get_base_url(image_type: str):
    match image_type:
        case 'vi':
            return 'i.ytimg.com'
        case 'ytc':
            return 'yt3.ggpht.com'

    raise Exception('No base url for image was found')

