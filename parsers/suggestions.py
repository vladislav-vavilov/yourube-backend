import requests
import json
import re

from parsers.common import random_proxy, user_agent


def get_suggestions(query: str):
    try:
        headers = {'User-Agent': user_agent.random}
        url = f'https://suggestqueries-clients6.youtube.com/complete/search?client=youtube&q={query}'
        response = requests.get(url, headers=headers, proxies=random_proxy)

        decoded_data = response.content.decode('utf-8')

        matched_suggestions_lists = re.search(r'\[\[".*\]\]', decoded_data)
        if matched_suggestions_lists:
            data = json.loads(matched_suggestions_lists.group())
            suggestions = list(set(i[0] for i in data))

            return suggestions

        return []
    except requests.exceptions.RequestException as e:
        print(f'Request error: {e}')
    except json.JSONDecodeError as e:
        print(f'Failed to decode JSON: {e}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')
