from typing import Union
from fastapi import FastAPI, HTTPException

from parsers.suggestions import get_suggestions
from parsers.search_results import get_search_results
from parsers.playlist import get_playlist
from parsers.channel import get_channel

app = FastAPI()


@app.get('/suggestions')
def suggestions(q: Union[str, None] = None):
    if not q:
        raise HTTPException(status_code=400, detail='Query param is required')

    suggestions = get_suggestions(q)
    return suggestions


@app.get('/search')
def search_results(q: Union[str, None] = None, continuation: Union[str, None] = None):
    if not (q or continuation):
        raise HTTPException(
            status_code=400, detail='Query or continuation param is required'
        )

    results = get_search_results(query=q, continuation=continuation)
    return results


@app.get('/playlists/{playlist_id}')
def playlist(playlist_id: str, continuation: Union[str, None] = None):
    results = get_playlist(id=playlist_id, continuation=continuation)
    return results


@app.get('/channels/{channel_id}')
def channel(channel_id: str, continuation: Union[str, None] = None):
    results = get_channel(id=channel_id, continuation=continuation)
    return results
