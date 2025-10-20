from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.anon.models.term_conversion import TermConversion


class ConversionRegistrationApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def create_registration_conversion(self, aid: str, term_id: str, user_token: str = None, user_provider: str = None, user_ref: str = None, tbc: str = None, pageview_id: str = None) -> ApiResponse[TermConversion]:
        _url_path = '/api/v3/conversion/registration/create'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'user_token': _encode_parameter(user_token),
            'user_provider': _encode_parameter(user_provider),
            'user_ref': _encode_parameter(user_ref),
            'term_id': _encode_parameter(term_id),
            'tbc': _encode_parameter(tbc),
            'pageview_id': _encode_parameter(pageview_id)
        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {

        }

        _body = None
        _files = None

        _request = self.config.http_client.build_request('GET',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, TermConversion)
        return _result

