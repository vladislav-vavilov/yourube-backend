from fake_useragent import UserAgent
from parsers.config import proxies

from random import randrange


user_agent = UserAgent(platforms='pc')
random_proxy = proxies[randrange(0, len(proxies))]


def parse_items(items):
    results = []
    for item in items:
        parsed_item = parse_item(item)

        if parsed_item:
            results.append(parsed_item)

    return results


def parse_item(item):
    '''Parse item depending on its type'''

    match list(item.keys())[0]:
        case 'videoRenderer':
            return parse_video_item(item['videoRenderer'])
        case 'playlistVideoRenderer':
            return parse_playlist_video_item(item['playlistVideoRenderer'])
        case 'playlistRenderer':
            return parse_playlist_item(item['playlistRenderer'])
        case 'channelRenderer':
            return parse_channel_item(item['channelRenderer'])
        case 'continuationItemRenderer':
            return parse_continuation_token(item['continuationItemRenderer'])
        case 'reelItemRenderer':
            pass


def parse_video_item(data):
    '''Parse video data'''
    try:
        video_info = {
            'url': f'/watch?v={data['videoId']}',
            'type': 'video' if 'isShort' not in data else 'shorts',
            'title': data['title']['runs'][0]['text'],
            'thumbnail': data['thumbnail']['thumbnails'][0]['url'],
            'uploadedDate': data.get('publishedTimeText', {}).get('simpleText', 'Unknown date'),
            'shortDescription': data['detailedMetadataSnippets'][0]['snippetText']['runs'][0]['text'] if 'detailedMetadataSnippets' in data else 'No description',
            'duration': data['lengthText']['simpleText'] if 'lengthText' in data else 'Unknown duration',
            'views': int(''.join(data.get('viewCountText', {}).get('simpleText', '0 views').replace(',', '').split()[:-1])),
            'uploaderVerified': 'ownerBadges' in data and any('VERIFIED' in badge['metadataBadgeRenderer']['style'] for badge in data['ownerBadges']),
            'isShort': 'isShort' in data
        }

        is_uploader_info = 'ownerText' in data

        if is_uploader_info:
            uploader_info = {
                'uploaderName': data['ownerText']['runs'][0]['text'],
                'uploaderUrl': f'/channel/{data['ownerText']['runs'][0]['navigationEndpoint']['browseEndpoint']['browseId']}',
                'uploaderAvatar': data['channelThumbnailSupportedRenderers']['channelThumbnailWithLinkRenderer']['thumbnail']['thumbnails'][0]['url'],
            }

            return video_info | uploader_info

        return video_info
    except (KeyError, IndexError) as e:
        print(f'Failed to parse video: {e}')


def parse_playlist_video_item(data):
    '''Parse playlist video data'''
    try:
        return {
            'url': f'/watch?v={data['videoId']}',
            'title': data['title']['runs'][0]['text'],
            'thumbnail': data['thumbnail']['thumbnails'][0]['url'],
            'uploadedDate': data['videoInfo']['runs'][0]['text'],
            'duration': data['lengthText']['simpleText'],
            'views': data['videoInfo']['runs'][2]['text'],
        }
    except (KeyError, IndexError) as e:
        print(f'Failed to parse playlist video: {e}')


def parse_playlist_item(data):
    '''Parse playlist data'''
    try:
        return {
            'url': f'/playlist?list={data['playlistId']}',
            'type': 'playlist',
            'name': data['title']['simpleText'],
            'thumbnail': data['thumbnails'][0]['thumbnails'][0]['url'],
            'uploaderName': data['shortBylineText']['runs'][0]['text'],
            'uploaderUrl': f'/channel/{data['shortBylineText']['runs'][0]['navigationEndpoint']['browseEndpoint']['browseId']}',
            'uploaderVerified': 'ownerBadges' in data and any('VERIFIED' in badge['metadataBadgeRenderer']['style'] for badge in data['ownerBadges']),
            'playlistType': data.get('playlistType', 'NORMAL').upper(),
            'videos': int(data['videoCount'])
        }
    except (KeyError, IndexError) as e:
        print(f'Failed to parse playlist item: {e}')


def parse_channel_item(data):
    '''Parse channel data'''
    try:
        return {
            'url': f'/channel/{data['channelId']}',
            'type': 'channel',
            'name': data['title']['simpleText'],
            'thumbnail': data['thumbnail']['thumbnails'][0]['url'],
            'description': data['descriptionSnippet']['runs'][0]['text'] if 'descriptionSnippet' in data else '',
            'subscribers': data['videoCountText']['simpleText'].replace(' subscribers', ''),
            'videos': int(data.get('videoCountText'[0], {}).get('runs', [{}])[0].get('text', '-1').replace(',', '')) if 'videoCountText' in data else -1,
            'verified': 'ownerBadges' in data and any('VERIFIED' in badge['metadataBadgeRenderer']['style'] for badge in data['ownerBadges'])
        }
    except (KeyError, IndexError) as e:
        print(f'Failed to parse channel item: {e}')


def parse_reel_item(data):
    try:
        return {
            'url': f'/shorts/{data['videoId']}',
            'type': 'shorts',
            'title': data['headline']['simpleText'],
            'thumbnail': data['thumbnail']['thumbnails'][0]['url'],
            'views': data['viewCountText']['simpleText'].replace(' views', '')
        }
    except (KeyError, IndexError) as e:
        print(f'Failed to parse reel item: {e}')


def parse_continuation_token(data):
    try:
        return data['continuationEndpoint']['continuationCommand']['token']
    except (KeyError, IndexError) as e:
        print(f'Failed to parse continuation token: {e}')


# def replace_image_base_url(image_url, new_base_url):
#    return new_base_url + '/'.join(image_url.split('/')[3:])
