import requests
import re
import json
import sys
from proxy import PROXY_HOST, PROXY_PORT, PROXY_USERNAME, PROXY_PASSWORD
from fake_useragent import UserAgent
from pprint import pprint

user_agent = UserAgent(platforms='pc')

proxies = {
    "http": f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}",
    "https": f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}",
}


def parse_video(data):
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
        "views": int(data.get('viewCountText', {}).get('simpleText', '0 views').replace(' views', '').replace(',', '')),
        "uploaderVerified": 'ownerBadges' in data and any('VERIFIED' in badge['metadataBadgeRenderer']['style'] for badge in data['ownerBadges']),
        "isShort": 'isShort' in data
    }


def parse_playlist(data):
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
    if 'videoRenderer' in item:
        return parse_video(item['videoRenderer'])
    elif 'playlistRenderer' in item:
        return parse_playlist(item['playlistRenderer'])
    elif 'channelRenderer' in item:
        return parse_channel(item['channelRenderer'])


def get_suggestions(query):
    headers = {"User-Agent": user_agent.random}
    url = f'https://suggestqueries-clients6.youtube.com/complete/search?client=youtube&q={query}'
    response = requests.get(url, headers=headers, proxies=proxies)

    decoded_data = response.content.decode('utf-8')

    matched_suggestions_lists = re.search(r'\[\[".*\]\]', decoded_data)
    if matched_suggestions_lists:
        data = json.loads(matched_suggestions_lists.group())
        suggestions = list(set(i[0] for i in data))

        return suggestions

    return []


def get_search_results(query):
    headers = {"User-Agent": user_agent.random}
    url = f"https://www.youtube.com/results?search_query={query}"

    response = requests.get(url, headers=headers, proxies=proxies)

    initial_data = re.search(
        r'var ytInitialData = ({.*?});</script>', response.text)

    if not initial_data:
        print("Unable to find initial data in the response.")
        return []

    data = json.loads(initial_data.group(1))

    search_results = []

    try:
        contents = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents']

        for content in contents:
            # Some sections might not have 'itemSectionRenderer', so we skip those
            if 'itemSectionRenderer' not in content:
                continue

            items = content['itemSectionRenderer']['contents']

            for item in items:
                parsed_item = parse_item(item)

                if parsed_item:
                    search_results.append(parsed_item)

    except KeyError as e:
        print(f"KeyError: {e} not found in the expected JSON structure.")
        return []

    return search_results


if __name__ == "__main__":
    query = sys.argv[1]
    results = get_search_results(query)
    # results = get_suggestions(query)
    pprint(results)
