import warnings

import httpx
import xmltodict

from ut_com.com import Com
from ut_com.log import Log
from ut_gen.utg import DoUri

warnings.filterwarnings("ignore")


class Content:

    @staticmethod
    def sh_dic(resp):
        content = resp.headers['Content-Type']
        a_content = content.split(';')
        d_content = {}
        d_content['content_type'] = a_content[0].strip()
        if len(a_content) > 1:
            d_content['charset'] = a_content[1].strip()
        Log.Eq.debug("resp.headers", resp.headers)
        Log.Eq.debug("d_content", d_content)
        return d_content

    @classmethod
    def sh(cls, resp):
        d_ct = cls.sh_dic(resp)
        Log.Eq.debug("d_ct", d_ct)
        match d_ct['content_type']:
            case 'application/json':
                content = resp.json()
            case 'text/plain':
                content = resp.text
            case 'text/xml':
                content = xmltodict.parse(resp.text)
            case 'text/html':
                content = resp.text
            case _:
                content = None
        return content


class Uri:

    @staticmethod
    def sh(uri, **kwargs):
        if uri is None:
            d_uri = kwargs.get('d_uri')
            Log.Eq.debug("d_uri", d_uri)
            uri = DicUri.sh(d_uri)
            Log.Eq.debug("uri", uri)
        return uri


class Kw:

    @staticmethod
    def sh(**kwargs):
        params = kwargs.get('params')
        data = kwargs.get('data')
        headers = kwargs.get('headers')
        auth = kwargs.get('auth')

        Log.Eq.debug("auth", auth)
        Log.Eq.debug("params", params)
        Log.Eq.debug("data", data)
        Log.Eq.debug("headers", headers)

        kw = {}
        if data is not None:
            kw['data'] = data
        if params is not None:
            kw['params'] = params
        if headers is not None:
            kw['headers'] = headers
        if auth is not None:
            kw['auth'] = auth
        Log.Eq.debug("kw", kw)
        return kw


class Session:

    @staticmethod
    def get(uri=None, **kwargs):
        uri = Uri.sh(uri, **kwargs)
        content = None
        kw = Kw.sh(**kwargs)
        try:
            if 'session' not in Com.App.reqs:
                Com.App.reqs.session = httpx.Session()
            resp = Com.App['reqs']['session'].get(uri, **kw)
            resp.raise_for_status()
            Log.Eq.debug("resp", resp)
            Log.Eq.debug("resp.headers", resp.headers)
            content = Content.sh(resp)
        except httpx.exceptions.HTTPError as e:
            # Need to check its an 404, 503, 500, 403 etc.
            # status_code = e.response.status_code
            Log.warning(e, exc_info=True)
        except Exception:
            # Log.error(e, exc_info=True)
            raise
        Log.Eq.debug("content", content)
        return content


class Request:

    @staticmethod
    def get(uri=None, **kwargs):
        uri = Request.Uri.sh(uri, **kwargs)
        content = None
        kw = Kw.sh(**kwargs)
        try:
            resp = httpx.get(uri, **kw)
            Log.Eq.debug(">>> kw", kw)
            Log.Eq.debug(">>> resp", resp)
            Log.Eq.debug(">>> resp.headers", resp.headers)
            resp.raise_for_status()
            content = Content.sh(resp)
        except httpx.exceptions.HTTPError as e:
            # Need to check its an 404, 503, 500, 403 etc.
            status_code = e.response.status_code
            Log.Eq.debug("e.response.status_code", status_code)
            Log.warning(e, exc_info=True)
        except Exception:
            # Log.error(e, exc_info=True)
            raise
        return content
        Log.Eq.debug("EEE content", content)
