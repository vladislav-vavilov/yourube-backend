import requests
import re
import json
from base64 import b64encode, b64decode
from proxy import proxies
from fake_useragent import UserAgent

user_agent = UserAgent(platforms='pc')


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
    url = f"https://www.youtube.com/results?search_query={query}"

    response = requests.get(url, headers=headers, proxies=proxies)

    try:
        data = get_initial_data(response)
        contents = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents']

        search_results, continuation_token = parse_contents(contents)
        context = json.dumps(get_context(response))
        encoded_context = b64encode(context.encode()).decode()

        return {'items': search_results, 'nextpage': f'{encoded_context}@{continuation_token}'}

    except KeyError as e:
        print(f"KeyError: {e} not found in the expected JSON structure.")
        return []


def get_continuation_search_results(context, token):
    '''Get the next page of search results'''

    headers = {"User-Agent": user_agent.random}
    url = 'https://www.youtube.com/youtubei/v1/search'

    decoded_context = json.loads(b64decode(context.encode()).decode())
    data = json.dumps({"context": decoded_context, "continuation": token})

    response = requests.post(url, data=data, headers=headers, proxies=proxies)
    response_json = response.json()
    data = response_json['onResponseReceivedCommands'][0]['appendContinuationItemsAction']['continuationItems']

    search_results, continuation_token = parse_contents(data)

    return {'items': search_results, 'nextpage': f'{context}@{continuation_token}'}


def parse_contents(contents):
    '''Parse search result items (videos, playlists, channels)'''

    results = []
    continuation_token = contents[1]['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']

    items = contents[0]['itemSectionRenderer']['contents']
    for item in items:
        parsed_item = parse_item(item)

        if parsed_item:
            results.append(parsed_item)

    return results, continuation_token


def get_initial_data(response):
    '''Get initial data from the response html'''

    initial_data_string = re.search(
        r'var ytInitialData = ({.*?});</script>', response.text)

    if not initial_data_string:
        raise Exception("Unable to find initial data in the response.")

    initial_data = json.loads(initial_data_string.group(1))
    return initial_data


def get_context(response):
    '''Get context from the response html'''

    context_string = re.search(r'ytcfg\.set\((\{.*?\})\)', response.text)

    if not context_string:
        raise Exception("Unable to find context in the response.")

    context = json.loads(context_string.group(1))['INNERTUBE_CONTEXT']

    return context


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
