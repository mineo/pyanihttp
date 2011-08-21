# coding: utf-8
# TODO parse characters
import xml.etree.ElementTree as ET
import requests
import StringIO
import model
import cache
import exceptions
import datetime

__all__ = ["search", "query", "QUERY_ANIME", "set_client",
           "QUERY_CATEGORIES"]# "CLIENT", "CLIENTVERSION"]

CLIENT = None
CLIENTVERSION = None

SEARCH_URL = "http://anisearch.outrance.pl?task=search&query=%s"
ANIDB_URL = \
"http://api.anidb.net:9001/httpapi?client=%s&clientver=%i&protover=1&request=%s"

#: Query type used for retrieving information about an anime
QUERY_ANIME = 1

#: Query type used to retrieve the list of categories
QUERY_CATEGORIES = 2

def set_client(name, version):
    """
    Set the `client` and `clientversion` parameters used in the HTTP request to
    the AniDB.
    """
    global CLIENT
    global CLIENTVERSION
    CLIENT = name
    CLIENTVERSION = version

def search(title, exact=False):
    """
    Search for an anime.

    :param title: The anime to search for
    :param exact: Boolean. Whether or not to only return exact matches
    :rtype: List of :class:`anidb.model.Anime`
    """
    if exact:
        title = "\\" + title
    result = requests.get(SEARCH_URL % title)
    return _handle_response(result.content)

def query(type=QUERY_ANIME, aid=None, **kwargs):
    """
    Query AniDB for information about the anime identified by *aid* or the
    complete list of categories.

    :param type: Either QUERY_CATEGORIES or QUERY_ANIME
    :param aid: If *type* is QUERY_ANIME, the aid of the anime
    :param kwargs: Any kwargs you want to pass to :func:`requests.get`
    :raises: ValueError if `anidb.CLIENT` or `anidb.CLIENTVERSION` are not set
    :rtype: :class:`anidb.model.Anime` or a list of
            :class:`anidb.model.Category`
    """
    if CLIENT is None or CLIENTVERSION is None:
        raise ValueError(
                "You need to assign values to both CLIENT and CLIENTVERSION")
    if type == QUERY_ANIME:
        if aid is None:
            raise TypeError("aid can't be None")
        else:
            cacheresult = cache.get(aid)
            if cacheresult is not None:
                return cacheresult

            response = \
                requests.get(ANIDB_URL % (CLIENT, CLIENTVERSION, "anime")
                        + "&aid=%i" % aid, **kwargs)
            result =_handle_response(response.content)
            cache.save(aid, result)
            return result
    elif type == QUERY_CATEGORIES:
        response = requests.get(ANIDB_URL % (CLIENT, CLIENTVERSION,
                                "categorylist"), **kwargs)
        return _handle_response(response.content)

def _handle_response(response):
    if response == "<error>Banned</error>":
        raise exceptions.BannedException()
    # TODO xml: is only used in lang, drop it
    t =  response.replace("xml:", "")
    tree = ET.ElementTree(file=StringIO.StringIO(t))
    return parse(tree.getroot())

def parse(tree):
    """
    Parse all the elements in an :class:`xml.etree.ElementTree.Element`
    """
    if tree.tag == "animetitles":
        result = []
        for elem in tree:
            t = parse(elem)
            result.append(t)
        return result
    elif tree.tag == "anime":
        return parse_element(tree)
    # TODO categorylist

def parse_element(elem):
    """docstring for parse_element"""
    if elem.tag == "anime":
        return parse_anime(elem)
    elif elem.tag == "categorylist":
        return parse(elem)
    elif elem.tag == "category":
        return parse_category(elem)

def parse_anime(anime):
    """
    Parses an anime Element

    :param anime: An anime :class:`xml.etree.ElementTree.Element`
    :rtype: :class:`anidb.model.Anime`
    """
    # Anisearch has "aid" attributes ... 
    if "aid" in anime.attrib:
        result = model.Anime(anime.attrib["aid"])
    # ... anidb has just "id"
    else:
        result = model.Anime(anime.attrib["id"])
    for elem in anime:
        # AniDB returns an element "titles" with lots of "title" subelements
        if elem.tag == "titles":
            for t_elem in elem:
                t = parse_title(t_elem)
                result.add_title(t)
        # AniSearch has "title" subelements on "anime"
        elif elem.tag == "title":
            t = parse_title(elem)
            result.add_title(t)
        elif elem.tag == "type":
            result.type = elem.text
        elif elem.tag == "startdate":
            y, m, d = elem.text.split("-")
            result.startdate = datetime.datetime(int(y), int(m), int(d))
        elif elem.tag == "enddate":
            y, m, d = elem.text.split("-")
            result.enddate = datetime.datetime(int(y), int(m), int(d))
        elif elem.tag == "episodecount":
            result.episodecount = elem.text
        elif elem.tag == "ratings":
            for r in elem:
                result.set_rating(r.tag, r.attrib["count"], float(r.text))
        elif elem.tag == "categories":
            for c in parse_categorylist(elem):
                result.add_category(c)
        elif elem.tag == "episodes":
            for e in elem:
                result.add_episode(parse_episode(e))
        elif elem.tag == "tags":
            for tag in parse_tags(elem):
                result.add_tag(tag)
    return result

def parse_categorylist(categorylist):
    for c in categorylist:
        yield parse_category(c)

def parse_category(category):
    """
    Parse a category element

    :param category: A category :class:`xml.etree.ElementTree.Element`
    :rtype: :class:`anidb.model.Category`
    """
    result = model.Category(category.attrib["id"])
    for elem in category:
        setattr(result, elem.tag, elem.text)
    if category.attrib["hentai"] == "true":
        result.hentai = True
    result.weight = category.attrib["weight"]
    if "parentid" in category.attrib:
        result.parentid = category.attrib["parentid"]
    return result

def parse_episode(episode):
    ep = model.Episode(episode.attrib["id"])
    for elem in episode:
        if elem.tag == "length":
            ep.length = elem.text
        elif elem.tag == "airdate":
            y, m, d = elem.text.split("-")
            ep.airdate = datetime.datetime(int(y), int(m), int(d))
        elif elem.tag == "rating":
            ep.set_rating(elem.attrib["votes"], elem.text)
        elif elem.tag == "title":
            t = parse_title(elem)
            ep.add_title(t)
        elif elem.tag == "epno":
            ep.epno = elem.text
    return ep

def parse_title(elem):
    """
    Parse a <title> element

    :rtype: :class:`anidb.model.Title`
    """
    t = model.Title(lang = elem.attrib["lang"],
              title = elem.text)
    if "type" in elem.attrib:
        t.type = elem.attrib["type"]
    if "exact" in elem.attrib:
        t.exact = True
    return t

def parse_tags(elem):
    for t in elem:
        yield parse_tag(t)

def parse_tag(elem):
    t = model.Tag(elem.attrib["id"])
    t.approval = elem.attrib["approval"]
    if elem.attrib["spoiler"].lower() == "true":
        t.spoiler = True
    for e in elem:
        setattr(t, e.tag, e.text)
    return t
