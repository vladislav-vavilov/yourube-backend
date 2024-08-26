import requests
from io import BytesIO
from parsers.common import proxies


def get_image(path):
    image_type = path.split('/')[0]
    base_url = get_base_url(image_type)

    if not base_url:
        raise Exception('No base url for image was found')

    url = f'https://{base_url}/{path}'
    response = requests.get(url=url, proxies=proxies)
    image_stream = BytesIO(response.content)

    return image_stream


def get_base_url(image_type):
    match image_type:
        case 'vi':
            return 'i.ytimg.com'
        case 'ytc':
            return 'yt3.ggpht.com'
