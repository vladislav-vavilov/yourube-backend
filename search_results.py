import requests
import json

from config import BASE_URL
from proxy import proxies
from utils import encode, decode
from common import user_agent, get_initial_data, get_context,  parse_items


filters = {
    'type': {
        'video': 'B',
        'playlist': 'D',
        'channel': 'C'
    },
    'sort': {
        'relevance': 'CAAsAhA',
        'date': 'CAISAhA',
        'views': 'CAMSAhA',
    },
    'duration': {
        'short': 'EgQQARgB',
        'middle': 'EgQQARgD',
        'long': 'EgQQARgC',
    },
    'date': {
        'hour':  'EgIIAQ%253D%253D',
        'today': 'EgQIAhAB',
        'week':  'EgQIAxAB',
        'month': 'EgQIBBAB',
        'year':  'EgQIBRAB',
    }
}


def get_search_results(query, nextpage=None):
    '''Get first or subsequent pages of search results'''

    try:
        if nextpage:
            context, token = nextpage.split('@')
            return get_continuation_search_results(context=context, token=token)
        else:
            return get_initial_search_results(query)
    except Exception as e:
        print(f'Error: {e}')


def get_initial_search_results(query):
    '''Get first page of search results'''

    headers = {"User-Agent": user_agent.random}
    url = f"{BASE_URL}/results?search_query={query}"

    response = requests.get(url, headers=headers, proxies=proxies)

    try:
        data = get_initial_data(response)
        contents = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents']

        continuation_token = get_continuation_token(contents[1])
        search_results = parse_items(
            contents[0]['itemSectionRenderer']['contents']
        )
        context = json.dumps(get_context(response))

        return {'items': search_results, 'nextpage': f'{encode(context)}@{continuation_token}'}

    except KeyError as e:
        print(f"KeyError: {e} not found in the expected JSON structure.")
        return []


def get_continuation_search_results(context, token):
    '''Get the next page of search results'''

    headers = {"User-Agent": user_agent.random}
    url = f'{BASE_URL}/youtubei/v1/search'

    decoded_context = json.loads(decode(context))
    data = json.dumps({"context": decoded_context, "continuation": token})

    response = requests.post(url, data=data, headers=headers, proxies=proxies)
    response_json = response.json()
    data = response_json['onResponseReceivedCommands'][0]['appendContinuationItemsAction']['continuationItems']

    continuation_token = get_continuation_token(data)
    search_results = parse_items(data[0]['itemSectionRenderer']['contents'])

    return {'items': search_results, 'nextpage': f'{context}@{continuation_token}'}


def get_continuation_token(content):
    return content['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']


def parse_video(data):
    '''Parse video data'''

    return {
        "url": f"/watch?v={data['videoId']}",
        "type": "video" if 'isShort' not in data else "shorts",
        "title": data['title']['runs'][0]['text'],
        "thumbnail": data['thumbnail']['thumbnails'][0]['url'],
        "uploaderName": data['ownerText']['runs'][0]['text'],
        "uploaderUrl": f"/channel/{data['ownerText']['runs'][0]['navigationEndpoint']['browseEndpoint']['browseId']}",
        "uploaderAvatar": data['channelThumbnailSupportedRenderers']['channelThumbnailWithLinkRenderer']['thumbnail']['thumbnails'][0]['url'],
        "uploadedDate": data.get('publishedTimeText', {}).get('simpleText', 'Unknown date'),
        "shortDescription": data['detailedMetadataSnippets'][0]['snippetText']['runs'][0]['text'] if 'detailedMetadataSnippets' in data else 'No description',
        "duration": data['lengthText']['simpleText'] if 'lengthText' in data else 'Unknown duration',
        "views": int(data.get('viewCountText', {}).get('simpleText', '0 views').replace(' views', '').replace(',', '').replace('No', '0')),
        "uploaderVerified": 'ownerBadges' in data and any('VERIFIED' in badge['metadataBadgeRenderer']['style'] for badge in data['ownerBadges']),
        "isShort": 'isShort' in data
    }


def parse_playlist(data):
    '''Parse playlist data'''

    return {
        "url": f"/playlist?list={data['playlistId']}",
        "type": "playlist",
        "name": data['title']['simpleText'],
        "thumbnail": data['thumbnails'][0]['thumbnails'][0]['url'],
        "uploaderName": data['shortBylineText']['runs'][0]['text'],
        "uploaderUrl": f"/channel/{data['shortBylineText']['runs'][0]['navigationEndpoint']['browseEndpoint']['browseId']}",
        "uploaderVerified": 'ownerBadges' in data and any('VERIFIED' in badge['metadataBadgeRenderer']['style'] for badge in data['ownerBadges']),
        "playlistType": data.get('playlistType', 'NORMAL').upper(),
        "videos": int(data['videoCount'])
    }


def parse_channel(data):
    '''Parse channel data'''

    return {
        "url": f"/channel/{data['channelId']}",
        "type": "channel",
        "name": data['title']['simpleText'],
        "thumbnail": data['thumbnail']['thumbnails'][0]['url'],
        "description": data['descriptionSnippet']['runs'][0]['text'] if 'descriptionSnippet' in data else '',
        "subscribers": data['videoCountText']['simpleText'].replace(' subscribers', ''),
        "videos": int(data.get('videoCountText'[0], {}).get('runs', [{}])[0].get('text', '-1').replace(',', '')) if 'videoCountText' in data else -1,
        "verified": 'ownerBadges' in data and any('VERIFIED' in badge['metadataBadgeRenderer']['style'] for badge in data['ownerBadges'])
    }


def parse_item(item):
    '''Parse item depending on its type'''

    if 'videoRenderer' in item:
        return parse_video(item['videoRenderer'])
    elif 'playlistRenderer' in item:
        return parse_playlist(item['playlistRenderer'])
    elif 'channelRenderer' in item:
        return parse_channel(item['channelRenderer'])
