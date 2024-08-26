from fastapi.responses import StreamingResponse

from typing import Union
from fastapi import FastAPI, HTTPException

from parsers.images import get_image
from parsers.suggestions import get_suggestions
from parsers.search_results import get_search_results
from parsers.playlist import get_playlist
from parsers.channel import get_channel

app = FastAPI()


@app.get('/suggestions')
def suggestions(q: Union[str, None] = None):
    try:
        if not q:
            raise HTTPException(
                status_code=400,
                detail='Query param is required'
            )

        return get_suggestions(q)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@app.get('/search')
def search_results(q: Union[str, None] = None, continuation: Union[str, None] = None):
    try:
        if not (q or continuation):
            raise HTTPException(
                status_code=400,
                detail='Query or continuation param is required'
            )

        return get_search_results(query=q, continuation=continuation)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@app.get('/playlists/{playlist_id}')
def playlist(playlist_id: str, continuation: Union[str, None] = None):
    try:
        return get_playlist(id=playlist_id, continuation=continuation)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@app.get('/channels/{channel_id}')
def channel(channel_id: str, continuation: Union[str, None] = None):
    try:
        return get_channel(id=channel_id, continuation=continuation)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@app.get('/images/{image_path:path}')
def image(image_path: str):
    try:
        image_stream = get_image(image_path)
        return StreamingResponse(image_stream, media_type=f'image/jpeg')
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
