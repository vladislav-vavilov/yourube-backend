import requests
from parsers.common import random_proxy


def get_image(path: str):
    try:
        image_type = path.split('/')[0]
        base_url = get_base_url(image_type)

        url = f'https://{base_url}/{path}'
        response = requests.get(url=url, proxies=random_proxy, stream=True)

        if response.status_code != 200:
            raise Exception('Failed to get image')

        return response
    except requests.exceptions.RequestException as e:
        print(f'Request error: {e}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')


def get_base_url(image_type: str):
    match image_type:
        case 'vi':
            return 'i.ytimg.com'
        case 'ytc':
            return 'yt3.ggpht.com'

    raise Exception('No base url for image was found')
