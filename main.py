from search_results import get_search_results
from playlist import get_playlist
from pprint import pprint
import sys

mock_id = 'PLgtFJ5i1fDDdF2KA__Y3ozwFSdNe9Tb3W'


mock_token = "4qmFsgJXEiRWTFBMNGNVeGVHa2NDOWdVZ3IzOVFfeUQ2di1iU3lNd0tQVUkaCGtnRURDTGNMmgIkVkxQTDRjVXhlR2tjQzlnVWdyMzlRX3lENnYtYlN5TXdLUFVJ"

if __name__ == "__main__":
    query = sys.argv[1]
    results = get_playlist(id=mock_id)
    pprint(results)
