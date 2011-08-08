CLIENT = None
CLIENTVERSION = None

def set_client(name, version):
    """
    Set the `client` and `clientversion` parameters used in the HTTP request to
    the AniDB.
    """
    CLIENT = name
    CLIENTVERSION = version
