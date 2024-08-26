import requests
import json

from parsers.config import BASE_URL, context
from parsers.common import proxies, user_agent, parse_item

channel_params = {
    'videos': 'EgZ2aWRlb3PyBgQKAjoA',
    'shorts': 'EgZzaG9ydHPyBgUKA5oBAA%3D%3D',
    'live': 'EgdzdHJlYW1z8gYECgJ6AA%3D%3D',
    'podcasts': 'Eghwb2RjYXN0c_IGBQoDugEA',
    'playlists': 'EglwbGF5bGlzdHPyBgQKAkIA',
    'community': 'Egljb21tdW5pdHnyBgQKAkoA',
}


def get_channel(id=None, continuation=None):
    try:
        headers = {'User-Agent': user_agent.random}
        url = f'{BASE_URL}/youtubei/v1/browse'

        data = json.dumps({
            'context': context,
            'browseId': id,
            'params': channel_params['videos'],
            'continuation': continuation
        })

        response = requests.post(
            url, data=data, headers=headers, proxies=proxies)

        if continuation:
            return parse_more_channel_items(response.json())
        elif id:
            return parse_channel(response.json())
    except Exception as e:
        print('Unable to get channel:', e)


def parse_channel_info(data):
    channel_info = data['header']['pageHeaderRenderer']['content']['pageHeaderViewModel']
    metadata = channel_info['metadata']['contentMetadataViewModel']['metadataRows']

    return {
        'title': channel_info['title']['dynamicTextViewModel']['text']['content'],
        'avatar': channel_info['image']['decoratedAvatarViewModel']['avatar']['avatarViewModel']['image']['sources'][2]['url'],
        'username': metadata[0]['metadataParts'][0]['text']['content'],
        'subscribers': metadata[1]['metadataParts'][0]['text']['content'].replace(' subscribers', ''),
        'videos': metadata[1]['metadataParts'][1]['text']['content'],
        'description': channel_info['description']['descriptionPreviewViewModel']['description']['content'],
        'banner': channel_info['banner']['imageBannerViewModel']['image']['sources'][2]['url'],
    }


def parse_channel(data):
    '''Parse channel info and initial items with continuation token'''

    channel_info = parse_channel_info(data)

    tabs = []
    items = []
    continuation = None

    for tab in data['contents']['twoColumnBrowseResultsRenderer']['tabs']:
        if 'tabRenderer' not in tab:
            continue

        tab_info = tab['tabRenderer']
        tab_title = tab_info['title']

        if tab_title not in ['Videos', 'Shorts']:
            continue

        tabs.append(tab_title)

        if 'content' in tab_info:
            tab_items = tab_info['content']['richGridRenderer']['contents']
            last_item = tab_items.pop()

            continuation = parse_item(last_item)
            items = parse_items(tab_items)

    data = {
        'tabs': tabs,
        'items': items,
        'continuation': continuation
    }

    return channel_info | data


def parse_more_channel_items(data):
    '''Parse channel videos from continuation response json'''

    items = data['onResponseReceivedActions'][0]['appendContinuationItemsAction']['continuationItems']
    continuation = parse_item(items.pop())

    return {
        'items': parse_items(items),
        'continuation': continuation
    }


def parse_items(items):
    results = []
    for item in items:
        tab_item_content = item['richItemRenderer']['content']
        results.append(parse_item(tab_item_content))

    return results
