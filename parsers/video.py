import requests
from pytubefix import YouTube

from parsers.common import user_agent, random_proxy
from parsers.config import BASE_URL


headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'User-Agent': user_agent.random,
}


def get_video(video_id: str):
    try:
        yt = YouTube(f'{BASE_URL}/watch?v={video_id}', proxies=random_proxy)
        stream = yt.streams.get_highest_resolution()

        if not stream:
            raise Exception('Unable to extract stream url')

        response = requests.get(
            url=stream.url, proxies=random_proxy, headers=headers, stream=True)

        return response
    except requests.exceptions.RequestException as e:
        print(f'Request error: {e}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')
