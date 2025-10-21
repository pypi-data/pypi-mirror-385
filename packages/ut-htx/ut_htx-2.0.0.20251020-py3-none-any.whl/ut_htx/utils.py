import warnings

from ut_com.log import Log

from ut_http.http_ import Client as Http_Client
from ut_http.requests_ import Request as Request_Request
from ut_http.requests_ import Session as Request_Session
from ut_http.urllib3s_ import Request as Urllib3_Request

warnings.filterwarnings("ignore")


class Tasks:
    """ Manage uri's
    """
    doc: TyDoC = {
        'Http_Client': Http_Client.get,
        'Urllib3_Request': Urllib3_Request.get,
        'Request_Request': Request_Request.get,
        'Request_Session': Request_Session.get,
    }

    @classmethod
    def get(cls, **kwargs):
        _get = cls.doc.get('httpmod')
        content = _get(**kwargs)
        LogEq.debug('content', content)
        return content
