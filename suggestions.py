import requests
import json
import re
from proxy import proxies
from common import user_agent


def get_suggestions(query):
    headers = {'User-Agent': user_agent.random}
    url = f'https://suggestqueries-clients6.youtube.com/complete/search?client=youtube&q={query}'
    response = requests.get(url, headers=headers, proxies=proxies)

    decoded_data = response.content.decode('utf-8')

    matched_suggestions_lists = re.search(r'\[\[".*\]\]', decoded_data)
    if matched_suggestions_lists:
        data = json.loads(matched_suggestions_lists.group())
        suggestions = list(set(i[0] for i in data))

        return suggestions

    return []
