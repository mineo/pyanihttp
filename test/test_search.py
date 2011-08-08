from anidb import query

def pytest_funcarg__search_anime(request):
    xml = \
    """<?xml version="1.0" encoding="UTF-8"?>
    <anime aid="0">
            <title type="main" lang="x-jat" exact="exact">Title1</title>
            <title type="syn" lang="x-jat">SynTitle</title>
    </anime>
    """
    return query._handle_response(xml)

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
