import requests
import json

from config import BASE_URL, context
from proxy import proxies
from common import user_agent, parse_items


def get_playlist(id=None, continuation=None):
    try:
        headers = {"User-Agent": user_agent.random}
        url = f'{BASE_URL}/youtubei/v1/browse'

        data = json.dumps({
            'context': context,
            'browseId': 'VL' + id if id else None,
            'continuation': continuation
        })

        response = requests.post(
            url, data=data, headers=headers, proxies=proxies)

        if id:
            return parse_playlist(response.json())
        elif continuation:
            return parse_playlist_continuation(response.json())

    except Exception as e:
        print('Unable to get playlist:', e)


def parse_playlist(data):
    playlist_info = data['header']['playlistHeaderRenderer']

    items = data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content'][
        'sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['playlistVideoListRenderer']['contents']

    continuation = get_continuation(items)
    videos = parse_items(items)

    return {
        'id': playlist_info['playlistId'],
        'title': playlist_info['title']['simpleText'],
        'videos': playlist_info['stats'][0]['runs'][0]['text'],
        'description': playlist_info['descriptionText']['simpleText'],
        'uploaderName': playlist_info['ownerText']['runs'][0]['text'],
        'views': playlist_info['stats'][1]['simpleText'].replace(' views', '').replace(',', ''),
        'banner': playlist_info['playlistHeaderBanner']['heroPlaylistThumbnailRenderer']['thumbnail']['thumbnails'][0]['url'],
        'relatedStreams': videos,
        'continuation': continuation
    }


def parse_playlist_continuation(data):
    items = data['onResponseReceivedActions'][0]['appendContinuationItemsAction']['continuationItems']

    videos = parse_items(items)
    continuation = get_continuation(items)

    return {
        'relatedStreams': videos,
        'continuation': continuation
    }


def get_continuation(items):
    if 'continuationItemRenderer' not in items[-1]:
        return

    return items[-1]['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']
