import warnings
from http.client import HTTPSConnection
import socket

from ut_log.log import Log, LogEq
from ut_obj.str import Str
from ut_dic.douri import DoUri

from typing import Any, TypedDict
TyPath = str


class TyDoUri(TypedDict):
    authority: str
    schema: str
    path: TyPath
    query: str


TyDic = dict[Any, Any]
TyHeaders = dict[str, Any | str | int]
TyStr = str
TyUri = str | bytes

TnAny = None | Any
TnDic = None | TyDic
TnDoUri = None | TyDoUri
TnHeaders = None | TyHeaders
TnStr = None | TyStr
TnUri = None | TyUri

warnings.filterwarnings("ignore")


class Client:

    @staticmethod
    def get(**kwargs) -> TnDic:
        d_uri: TnDoUri = kwargs.get('d_uri')
        if not d_uri:
            return None
        headers: TnHeaders = kwargs.get('headers')
        if headers is None:
            return None
        authority: TnStr = d_uri.get('authority')
        if authority is None:
            return None

        params: TnDic = kwargs.get('params')
        _uri: TnUri = DoUri.sh_uri_by_params(d_uri, params)
        if _uri is None:
            return None
        data = kwargs.get('data')
        try:
            connection = HTTPSConnection(authority, timeout=10)
            LogEq.debug("data", data)
            LogEq.debug("headers", headers)
            LogEq.debug("d_uri", d_uri)
            if isinstance(_uri, bytes):
                _uri_str: TyStr = f"{_uri!r}"
            connection.request("GET", _uri_str, data, headers)
            response = connection.getresponse()
            _data: bytes | str = response.read()
            d_data: TyDic = Str.sh_dic(_data)
            connection.close()
            LogEq.debug("d_data", d_data)
        except socket.timeout:
            Log.error("connection's timeout: 10 expired")
            raise
        except Exception:
            raise
        return d_data
