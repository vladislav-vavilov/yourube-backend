import requests
import json

from config import BASE_URL, context
from proxy import proxies
from common import user_agent


def get_channel(id=None, continuation=None):
    try:
        headers = {"User-Agent": user_agent.random}
        url = f'{BASE_URL}/youtubei/v1/browse'

        data = json.dumps({
            'context': context,
            'browseId': id,
            'continuation': continuation
        })

        response = requests.post(
            url, data=data, headers=headers, proxies=proxies)

        return parse_channel(response.json())

    except Exception as e:
        print('Unable to get channel:', e)


def parse_channel(data):
    channel_info = data['header']['pageHeaderRenderer']['content']['pageHeaderViewModel']
    metadata = channel_info['metadata']['contentMetadataViewModel']['metadataRows']

    continuation = None
    videos = None

    return {
        'title': channel_info['title']['dynamicTextViewModel']['text']['content'],
        'avatar': channel_info['image']['decoratedAvatarViewModel']['avatar']['avatarViewModel']['image']['sources'][2]['url'],
        'username': metadata[0]['metadataParts'][0]['text']['content'],
        'subscribers': metadata[1]['metadataParts'][0]['text']['content'].replace(' subscribers', ''),
        'videos': metadata[1]['metadataParts'][1]['text']['content'],
        'description': channel_info['description']['descriptionPreviewViewModel']['description']['content'],
        'banner': channel_info['banner']['imageBannerViewModel']['image']['sources'][2]['url'],
        'relatedStreams': videos,
        'continuation': continuation
    }
