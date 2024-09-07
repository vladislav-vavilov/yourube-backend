import requests
import json

from parsers.config import BASE_URL, context
from parsers.common import random_proxy, user_agent, parse_items


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


def get_search_results(query=None, continuation=None):
    '''Get first or subsequent pages of search results'''

    try:
        headers = {'User-Agent': user_agent.random}
        url = f'{BASE_URL}/youtubei/v1/search'

        data = json.dumps({
            'context': context,
            'query': query,
            'continuation': continuation
        })

        response = requests.post(
            url, data=data, headers=headers, proxies=random_proxy)

        if continuation:
            contents = response.json()[
                'onResponseReceivedCommands'][0]['appendContinuationItemsAction']['continuationItems']
            return parse_search_results(contents)
        elif query:
            contents = response.json()['contents']['twoColumnSearchResultsRenderer']['primaryContents'][
                'sectionListRenderer']['contents']
            return parse_search_results(contents)

    except Exception as e:
        print('Unable to get search results:', e)


def parse_search_results(contents):
    items = parse_items(contents[0]['itemSectionRenderer']['contents'])

    return {
        'items': items,
        'continuation': get_continuation_token(contents[1])
    }


def get_continuation_token(content):
    return content['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']
