from search_results import get_search_results
from pprint import pprint
import sys

if __name__ == "__main__":
    query = sys.argv[1]
    results = get_search_results(query)
    # results = get_suggestions(query)
    pprint(results)
