import re
import json
from fake_useragent import UserAgent


user_agent = UserAgent(platforms='pc')


def get_initial_data(response):
    '''Get initial data from the response html'''

    initial_data_string = re.search(
        r'var ytInitialData\s=\s(.*?);</script>', response.text)

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


def parse_items(items):
    results = []
    for item in items:
        parsed_item = parse_item(item)

        if parsed_item:
            results.append(parsed_item)

    return results


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


def parse_playlist_video(data):
    '''Parse playlist video data'''

    return {
        'url': f'/watch?v={data["videoId"]}',
        'title': data['title']['runs'][0]['text'],
        'thumbnail': data['thumbnail']['thumbnails'][0]['url'],
        'uploaderName': data['shortBylineText']['runs'][0]['text'],
        'views': data['videoInfo']['runs'][0]['text'].replace(' views', '').replace(',', '').replace('No', '0'),
        'uploadedDate': data['videoInfo']['runs'][2]['text'],
        'duration': data['lengthSeconds']
    }


def parse_item(item):
    '''Parse item depending on its type'''

    if 'videoRenderer' in item:
        return parse_video(item['videoRenderer'])
    elif 'playlistRenderer' in item:
        return parse_playlist(item['playlistRenderer'])
    elif 'channelRenderer' in item:
        return parse_channel(item['channelRenderer'])
    elif 'playlistVideoRenderer' in item:
        return parse_playlist_video(item['playlistVideoRenderer'])
