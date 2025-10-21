from typing import Any

import warnings
import httpx
import xmltodict

from ut_log.log import Log, LogEq
# from ut_http import utils as ut

warnings.filterwarnings("ignore")

TyResponse = httpx.Response
TyContent = str
TyArr = list[Any]
TyDic = dict[Any, Any]
TyUri = str
TyDoUri = dict[Any, TyUri]

TnContent = None | TyContent
TnDic = None | TyDic
TnUri = None | TyUri


class Response:

    @staticmethod
    def sh_dic(response: TyResponse) -> TyDic:
        d_response: TyDic = {}
        d_response['status_code'] = response.status_code
        # Accessing attributes
        if response.status_code != httpx.codes.OK:
            return d_response
        d_response['headers'] = response.headers
        # a_content: TyArr = content.split(';')
        # if len(a_content) > 0:
        #     d_content['content_type'] = a_content[0].strip()
        # if len(a_content) > 1:
        #     d_content_type['charset'] = a_content[1].strip()
        match response.headers.get('Content-Type'):
            case 'application/json':
                d_response['json'] = response.json()
            case 'text/plain':
                d_response['text'] = response.text
            case 'text/xml':
                d_response['text'] = response.text
            case 'text/html':
                d_response['text'] = xmltodict.parse(response.text)

        LogEq.debug("d_response", d_response)
        return d_response


class DoReqs:

    @staticmethod
    def sh(**kwargs) -> TyDic:
        params: TnDic = kwargs.get('params')
        data = kwargs.get('data')
        headers: TnDic = kwargs.get('headers')
        auth = kwargs.get('auth')

        LogEq.debug("auth", auth)
        LogEq.debug("params", params)
        LogEq.debug("data", data)
        LogEq.debug("headers", headers)

        doreqs = {}
        if data is not None:
            doreqs['data'] = data
        if params is not None:
            doreqs['params'] = params
        if headers is not None:
            doreqs['headers'] = headers
        if auth is not None:
            doreqs['auth'] = auth
        LogEq.debug("doreqs", doreqs)
        return doreqs


class Request:

    @staticmethod
    def get(uri: TnUri, **kwargs) -> TyDic:
        if not uri:
            return {}
        _doreqs: TyDic = DoReqs.sh(**kwargs)
        LogEq.debug("doreqs", _doreqs)
        try:
            _response: TyResponse = httpx.get(uri, **_doreqs)
            LogEq.debug("_response", _response)
            LogEq.debug("_response.headers", _response.headers)
            # Raise an httpx.HTTPStatusError for error responses
            d_response = Response.sh_dic(_response)
            _response.raise_for_status()
        except httpx.HTTPError as exc:
            # Need to check its an 404, 503, 500, 403 etc.
            LogEq.debug("response.status_code", _response.status_code)
            Log.warning(exc, exc_info=True)
        except Exception as exc:
            Log.error(exc, exc_info=True)
            raise
        LogEq.debug("d_response", d_response)
        return d_response

    @staticmethod
    def post(uri: TnUri, **kwargs) -> TyDic:
        if not uri:
            return {}
        _doreqs: TyDoReqs = DoReqs.sh(**kwargs)
        LogEq.debug("_doreqs", _doreqs)
        try:
            _response: TyResponse = httpx.post(uri, **_doreqs)
            LogEq.debug("_response", _response)
            LogEq.debug("_response.headers", _response.headers)
            # Raise an httpx.HTTPStatusError for error responses
            d_response = Response.sh_dic(_response)
            _response.raise_for_status()
        except httpx.HTTPError as exc:
            # Need to check its an 404, 503, 500, 403 etc.
            LogEq.debug("response.status_code", _response.status_code)
            Log.warning(exc, exc_info=True)
        except Exception as exc:
            Log.error(exc, exc_info=True)
            raise
        LogEq.debug("d_response", d_response)
        return d_response
