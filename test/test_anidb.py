import pytest
import anidb.exceptions
import datetime

from anidb import query


def pytest_funcarg__anidb_anime(request):
    xml = \
    """<?xml version="1.0" encoding="UTF-8"?>
    <anime id="0" restricted = "false">
        <type>TV Series</type>
        <episodecount>1</episodecount>
        <startdate>1990-01-01</startdate>
        <enddate>1990-01-02</enddate>
        <ratings>
            <permanent count="7">1.0</permanent>
        </ratings>
        <categories>
            <category id="1" parentid="2" hentai="true" weight="100">
                <name>test</name>
                <description>test category</description>
            </category>
        </categories>
        <episodes>
            <episode id="1">
                <epno>1</epno>
                <length>2</length>
                <airdate>1999-01-01</airdate>
                <rating votes="12">1.0</rating>
                <title xml:lang="en">fooep</title>
            </episode>
        </episodes>
    </anime>
    """
    return query._handle_response(xml)

def test_banned():
    xml = "<error>Banned</error>"
    with pytest.raises(anidb.exceptions.BannedException):
        query._handle_response(xml)

def test_general(anidb_anime):
    assert anidb_anime.id == 0
    assert anidb_anime.type == "TV Series"
    assert anidb_anime.episodecount == 1

def test_ratings(anidb_anime):
    assert anidb_anime.ratings["permanent"]["count"] == 7
    assert anidb_anime.ratings["permanent"]["rating"] == 1.0

    assert anidb_anime.ratings["temporary"]["count"] is None
    assert anidb_anime.ratings["temporary"]["rating"] is None

def test_categories(anidb_anime):
    assert len(anidb_anime.categories) == 1
    assert anidb_anime.categories[0].hentai

def test_dates(anidb_anime):
    startdate = datetime.datetime(1990,1,1)
    enddate = datetime.datetime(1990,1,2)

    assert startdate == anidb_anime.startdate
    assert enddate == anidb_anime.enddate

def test_episodes(anidb_anime):
    assert len(anidb_anime.episodes) == 1
    assert 1 in anidb_anime.episodes.keys()
