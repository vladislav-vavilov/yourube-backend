from fastapi.responses import StreamingResponse

from typing import Union
from fastapi import FastAPI, HTTPException

from parsers.image import get_image
from parsers.suggestions import get_suggestions
from parsers.search_results import get_search_results
from parsers.playlist import get_playlist
from parsers.channel import get_channel
from parsers.video import get_video


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
def stream_image(image_path: str):
    try:
        image = get_image(image_path)

        if not image:
            return HTTPException(status_code=404, detail='Image was not found')

        return StreamingResponse(image, media_type='image/jpeg')
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@app.get('/videos/{video_id}')
def stream_video(video_id: str):
    try:
        video = get_video(video_id)

        if not video:
            return HTTPException(status_code=404, detail='Video was not found')

        headers = {
            'Content-length': video.headers['Content-Length'],
            'Accept-Ranges': video.headers.get('Accept-Ranges', 'none'),
        }

        return StreamingResponse(video, media_type='video/mp4', headers=headers)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
