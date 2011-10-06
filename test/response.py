class Response(object):
    def __init__(self, xml, code=200):
        self.content = xml
        self.status_code = code
