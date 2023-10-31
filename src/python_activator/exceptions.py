from fastapi import HTTPException


class EndpointNotFoundError(HTTPException):
    def __init__(self, e):
        self.status_code = 404
        self.title = __class__.__name__
        self.detail = repr(e)


class KONotFoundError(HTTPException):
    def __init__(self, e):
        self.status_code = 404
        self.title = __class__.__name__
        self.detail = repr(e)


class InvalidInputParameterError(HTTPException):
    def __init__(self, e):
        self.status_code = 500
        self.title = self.__class__.__name__
        self.detail = repr(e)
