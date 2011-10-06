from anidb.query import _handle_response
from test.response import Response

def test_codes():
    r = Response("", 404)
    anime = _handle_response(r)
    assert anime is None
