from anidb.query import _handle_response
from test.response import Response

def pytest_funcarg__search_anime(request):
    response = Response(\
    """<?xml version="1.0" encoding="UTF-8"?>
    <anime aid="0">
            <title type="main" lang="x-jat" exact="exact">Title1</title>
            <title type="syn" lang="x-jat">SynTitle</title>
    </anime>
    """)
    return _handle_response(response)

def test_search_xml(search_anime):
    assert search_anime.id == 0
    assert len(search_anime.titles["x-jat"]) == 2

    for lang, titles in search_anime.titles.items():
        for title in titles:
            assert lang == "x-jat"
            assert title.type is not None

            if title.type == "main":
                assert title.exact
            else:
                assert title.type == "syn"
                assert not title.exact
