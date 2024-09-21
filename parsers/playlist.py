import requests
import json

from parsers.config import BASE_URL, context
from parsers.common import random_proxy, user_agent, parse_item, parse_items

from typing import Optional


def get_playlist(id: Optional[str] = None, continuation: Optional[str] = None):
    try:
        headers = {'User-Agent': user_agent.random}
        url = f'{BASE_URL}/youtubei/v1/browse'

        data = json.dumps({
            'context': context,
            'browseId': f'VL{id}' if id else None,
            'continuation': continuation
        })

        response = requests.post(
            url, data=data, headers=headers, proxies=random_proxy)

        if continuation:
            return parse_more_playlist_videos(response.json())
        elif id:
            return parse_playlist(response.json())
    except requests.exceptions.RequestException as e:
        print(f'Request error: {e}')
    except KeyError as e:
        print(f'Missing expected data in response: {e}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')


def parse_playlist(data):
    try:
        playlist_info = data['header']['playlistHeaderRenderer']

        items = data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content'][
            'sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['playlistVideoListRenderer']['contents']

        continuation = get_continuation(items)
        videos = parse_items(items)

        return {
            'id': playlist_info['playlistId'],
            'title': playlist_info['title']['simpleText'],
            'videos': playlist_info['stats'][0]['runs'][0]['text'],
            'description': playlist_info.get('descriptionText', {}).get('simpleText', None),
            'uploaderName': playlist_info['ownerText']['runs'][0]['text'],
            'views': playlist_info['stats'][1]['simpleText'].replace(' views', '').replace(',', ''),
            'banner': playlist_info['playlistHeaderBanner']['heroPlaylistThumbnailRenderer']['thumbnail']['thumbnails'][0]['url'],
            'relatedStreams': videos,
            'continuation': continuation
        }
    except (KeyError, IndexError) as e:
        print(f'Failed to parse playlist: {e}')


def parse_more_playlist_videos(data):
    try:
        items = data['onResponseReceivedActions'][0]['appendContinuationItemsAction']['continuationItems']

        videos = parse_items(items)
        continuation = get_continuation(items)

        return {
            'relatedStreams': videos,
            'continuation': continuation
        }
    except (KeyError, IndexError) as e:
        print(f'Failed to parse more playlist videos: {e}')


def get_continuation(items):
    if 'continuationItemRenderer' not in items[-1]:
        return

    return parse_item(items[-1])
