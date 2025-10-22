from typing import Any

from pydantic import Field, StrictFloat, StrictInt, StrictStr, validate_call
from typing import Annotated

from royal_mail_click_and_drop.models.manifest_details_response import ManifestDetailsResponse
from royal_mail_click_and_drop.models.manifest_orders_response import ManifestOrdersResponse
from royal_mail_click_and_drop.api_client import ApiClient, RequestSerialized
from royal_mail_click_and_drop.api_response import ApiResponse
from royal_mail_click_and_drop.rest import RESTResponseType


class ManifestsApi:
    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client

    @validate_call
    def get_manifest_async(
        self,
        manifest_identifier: Annotated[
            StrictInt,
            Field(
                description='The manifest number returned from the initial ‘Manifest eligible orders’ endpoint call'
            ),
        ],
        _request_timeout: None | Annotated[StrictFloat, Field(gt=0)] | tuple[Annotated[StrictFloat, Field(gt=0)], Annotated[StrictFloat, Field(gt=0)]] = None,
        _request_auth: dict[StrictStr, Any] | None = None,
        _content_type: StrictStr | None = None,
        _headers: dict[StrictStr, Any] | None = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ManifestDetailsResponse:
        """Get manifest

        Retrieve manifest paperwork for a previously successful ‘Manifest eligible orders’ endpoint call

        :param manifest_identifier: The manifest number returned from the initial ‘Manifest eligible orders’ endpoint call (required)
        :type manifest_identifier: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """

        _param = self._get_manifest_async_serialize(
            manifest_identifier=manifest_identifier,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index,
        )

        _response_types_map: dict[str, str | None] = {
            '200': 'ManifestDetailsResponse',
            '400': 'ManifestErrorsResponse',
            '401': None,
            '403': None,
            '404': None,
            '500': 'ManifestErrorsResponse',
        }
        response_data = self.api_client.call_api(*_param, _request_timeout=_request_timeout)
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data

    @validate_call
    def get_manifest_async_with_http_info(
        self,
        manifest_identifier: Annotated[
            StrictInt,
            Field(
                description='The manifest number returned from the initial ‘Manifest eligible orders’ endpoint call'
            ),
        ],
        _request_timeout: None | Annotated[StrictFloat, Field(gt=0)] | tuple[Annotated[StrictFloat, Field(gt=0)], Annotated[StrictFloat, Field(gt=0)]] = None,
        _request_auth: dict[StrictStr, Any] | None = None,
        _content_type: StrictStr | None = None,
        _headers: dict[StrictStr, Any] | None = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[ManifestDetailsResponse]:
        """Get manifest

        Retrieve manifest paperwork for a previously successful ‘Manifest eligible orders’ endpoint call

        :param manifest_identifier: The manifest number returned from the initial ‘Manifest eligible orders’ endpoint call (required)
        :type manifest_identifier: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """

        _param = self._get_manifest_async_serialize(
            manifest_identifier=manifest_identifier,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index,
        )

        _response_types_map: dict[str, str | None] = {
            '200': 'ManifestDetailsResponse',
            '400': 'ManifestErrorsResponse',
            '401': None,
            '403': None,
            '404': None,
            '500': 'ManifestErrorsResponse',
        }
        response_data = self.api_client.call_api(*_param, _request_timeout=_request_timeout)
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )

    @validate_call
    def get_manifest_async_without_preload_content(
        self,
        manifest_identifier: Annotated[
            StrictInt,
            Field(
                description='The manifest number returned from the initial ‘Manifest eligible orders’ endpoint call'
            ),
        ],
        _request_timeout: None | Annotated[StrictFloat, Field(gt=0)] | tuple[Annotated[StrictFloat, Field(gt=0)], Annotated[StrictFloat, Field(gt=0)]] = None,
        _request_auth: dict[StrictStr, Any] | None = None,
        _content_type: StrictStr | None = None,
        _headers: dict[StrictStr, Any] | None = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Get manifest

        Retrieve manifest paperwork for a previously successful ‘Manifest eligible orders’ endpoint call

        :param manifest_identifier: The manifest number returned from the initial ‘Manifest eligible orders’ endpoint call (required)
        :type manifest_identifier: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """

        _param = self._get_manifest_async_serialize(
            manifest_identifier=manifest_identifier,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index,
        )

        _response_types_map: dict[str, str | None] = {
            '200': 'ManifestDetailsResponse',
            '400': 'ManifestErrorsResponse',
            '401': None,
            '403': None,
            '404': None,
            '500': 'ManifestErrorsResponse',
        }
        response_data = self.api_client.call_api(*_param, _request_timeout=_request_timeout)
        return response_data.response

    def _get_manifest_async_serialize(
        self,
        manifest_identifier,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:
        _auth_settings, _body_params, _collection_formats, _files, _form_params, _header_params, _host, _path_params, _query_params = self.manifest_get_2(
            _headers,
            manifest_identifier
        )

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/manifests/{manifestIdentifier}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth,
        )

    def manifest_get_2(self, _headers, manifest_identifier):
        _body_params, _collection_formats, _files, _form_params, _header_params, _host, _path_params, _query_params = self.manifest_get3(
            _headers
        )
        # process the path parameters
        if manifest_identifier is not None:
            _path_params['manifestIdentifier'] = manifest_identifier
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(['application/json'])
        # authentication setting
        _auth_settings: list[str] = ['Bearer']
        return _auth_settings, _body_params, _collection_formats, _files, _form_params, _header_params, _host, _path_params, _query_params

    @validate_call
    def manifest_eligible_async(
        self,
        _request_timeout: None | Annotated[StrictFloat, Field(gt=0)] | tuple[Annotated[StrictFloat, Field(gt=0)], Annotated[StrictFloat, Field(gt=0)]] = None,
        _request_auth: dict[StrictStr, Any] | None = None,
        _content_type: StrictStr | None = None,
        _headers: dict[StrictStr, Any] | None = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ManifestOrdersResponse:
        """Manifest eligible orders

        Manifest all orders in 'Label Generated' and 'Despatched' statuses and return manifest paperwork where possible

        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """

        _param = self._manifest_eligible_async_serialize(
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index,
        )

        _response_types_map: dict[str, str | None] = {
            '201': 'ManifestOrdersResponse',
            '202': 'ManifestOrdersResponse',
            '400': 'ManifestErrorsResponse',
            '401': None,
            '403': None,
            '404': None,
            '500': 'ManifestErrorsResponse',
        }
        response_data = self.api_client.call_api(*_param, _request_timeout=_request_timeout)
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data

    @validate_call
    def manifest_eligible_async_with_http_info(
        self,
        _request_timeout: None | Annotated[StrictFloat, Field(gt=0)] | tuple[Annotated[StrictFloat, Field(gt=0)], Annotated[StrictFloat, Field(gt=0)]] = None,
        _request_auth: dict[StrictStr, Any] | None = None,
        _content_type: StrictStr | None = None,
        _headers: dict[StrictStr, Any] | None = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[ManifestOrdersResponse]:
        """Manifest eligible orders

        Manifest all orders in 'Label Generated' and 'Despatched' statuses and return manifest paperwork where possible

        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """

        _param = self._manifest_eligible_async_serialize(
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index,
        )

        _response_types_map: dict[str, str | None] = {
            '201': 'ManifestOrdersResponse',
            '202': 'ManifestOrdersResponse',
            '400': 'ManifestErrorsResponse',
            '401': None,
            '403': None,
            '404': None,
            '500': 'ManifestErrorsResponse',
        }
        response_data = self.api_client.call_api(*_param, _request_timeout=_request_timeout)
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )

    @validate_call
    def manifest_eligible_async_without_preload_content(
        self,
        _request_timeout: None | Annotated[StrictFloat, Field(gt=0)] | tuple[Annotated[StrictFloat, Field(gt=0)], Annotated[StrictFloat, Field(gt=0)]] = None,
        _request_auth: dict[StrictStr, Any] | None = None,
        _content_type: StrictStr | None = None,
        _headers: dict[StrictStr, Any] | None = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Manifest eligible orders

        Manifest all orders in 'Label Generated' and 'Despatched' statuses and return manifest paperwork where possible

        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """

        _param = self._manifest_eligible_async_serialize(
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index,
        )

        _response_types_map: dict[str, str | None] = {
            '201': 'ManifestOrdersResponse',
            '202': 'ManifestOrdersResponse',
            '400': 'ManifestErrorsResponse',
            '401': None,
            '403': None,
            '404': None,
            '500': 'ManifestErrorsResponse',
        }
        response_data = self.api_client.call_api(*_param, _request_timeout=_request_timeout)
        return response_data.response

    def _manifest_eligible_async_serialize(
        self,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:
        _body_params, _collection_formats, _files, _form_params, _header_params, _host, _path_params, _query_params = self.manifest_get3(
            _headers
        )
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(['application/json'])
        _auth_settings: list[str] = ['Bearer']

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/manifests',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth,
        )

    def manifest_get3(self, _headers):
        _host = self.manifest_get()
        _collection_formats: dict[str, str] = {}
        _path_params: dict[str, str] = {}
        _query_params: list[tuple[str, str]] = []
        _header_params: dict[str, str | None] = _headers or {}
        _form_params: list[tuple[str, str]] = []
        _files: dict[str, str | bytes | list[str] | list[bytes] | list[tuple[str, bytes]]] = {}
        _body_params: bytes | None = None
        return _body_params, _collection_formats, _files, _form_params, _header_params, _host, _path_params, _query_params

    def manifest_get(self):
        _host = None
        return _host

    @validate_call
    def retry_manifest_async(
        self,
        manifest_identifier: Annotated[
            StrictInt,
            Field(
                description='The manifest number returned from the initial ‘Manifest eligible orders’ endpoint call'
            ),
        ],
        _request_timeout: None | Annotated[StrictFloat, Field(gt=0)] | tuple[Annotated[StrictFloat, Field(gt=0)], Annotated[StrictFloat, Field(gt=0)]] = None,
        _request_auth: dict[StrictStr, Any] | None = None,
        _content_type: StrictStr | None = None,
        _headers: dict[StrictStr, Any] | None = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ManifestOrdersResponse:
        """Retry manifest

        Retry a manifest operation if the eligible orders were not able to be successfully processed in the initial ‘Manifest eligible orders’ endpoint call and return manifest paperwork where possible

        :param manifest_identifier: The manifest number returned from the initial ‘Manifest eligible orders’ endpoint call (required)
        :type manifest_identifier: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """

        _param = self._retry_manifest_async_serialize(
            manifest_identifier=manifest_identifier,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index,
        )

        _response_types_map: dict[str, str | None] = {
            '201': 'ManifestOrdersResponse',
            '202': 'ManifestOrdersResponse',
            '400': 'ManifestErrorsResponse',
            '401': None,
            '403': None,
            '404': None,
            '500': 'ManifestErrorsResponse',
        }
        response_data = self.api_client.call_api(*_param, _request_timeout=_request_timeout)
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data

    @validate_call
    def retry_manifest_async_with_http_info(
        self,
        manifest_identifier: Annotated[
            StrictInt,
            Field(
                description='The manifest number returned from the initial ‘Manifest eligible orders’ endpoint call'
            ),
        ],
        _request_timeout: None | Annotated[StrictFloat, Field(gt=0)] | tuple[Annotated[StrictFloat, Field(gt=0)], Annotated[StrictFloat, Field(gt=0)]] = None,
        _request_auth: dict[StrictStr, Any] | None = None,
        _content_type: StrictStr | None = None,
        _headers: dict[StrictStr, Any] | None = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[ManifestOrdersResponse]:
        """Retry manifest

        Retry a manifest operation if the eligible orders were not able to be successfully processed in the initial ‘Manifest eligible orders’ endpoint call and return manifest paperwork where possible

        :param manifest_identifier: The manifest number returned from the initial ‘Manifest eligible orders’ endpoint call (required)
        :type manifest_identifier: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """

        _param = self._retry_manifest_async_serialize(
            manifest_identifier=manifest_identifier,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index,
        )

        _response_types_map: dict[str, str | None] = {
            '201': 'ManifestOrdersResponse',
            '202': 'ManifestOrdersResponse',
            '400': 'ManifestErrorsResponse',
            '401': None,
            '403': None,
            '404': None,
            '500': 'ManifestErrorsResponse',
        }
        response_data = self.api_client.call_api(*_param, _request_timeout=_request_timeout)
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )

    @validate_call
    def retry_manifest_async_without_preload_content(
        self,
        manifest_identifier: Annotated[
            StrictInt,
            Field(
                description='The manifest number returned from the initial ‘Manifest eligible orders’ endpoint call'
            ),
        ],
        _request_timeout: None | Annotated[StrictFloat, Field(gt=0)] | tuple[Annotated[StrictFloat, Field(gt=0)], Annotated[StrictFloat, Field(gt=0)]] = None,
        _request_auth: dict[StrictStr, Any] | None = None,
        _content_type: StrictStr | None = None,
        _headers: dict[StrictStr, Any] | None = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Retry manifest

        Retry a manifest operation if the eligible orders were not able to be successfully processed in the initial ‘Manifest eligible orders’ endpoint call and return manifest paperwork where possible

        :param manifest_identifier: The manifest number returned from the initial ‘Manifest eligible orders’ endpoint call (required)
        :type manifest_identifier: int
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """

        _param = self._retry_manifest_async_serialize(
            manifest_identifier=manifest_identifier,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index,
        )

        _response_types_map: dict[str, str | None] = {
            '201': 'ManifestOrdersResponse',
            '202': 'ManifestOrdersResponse',
            '400': 'ManifestErrorsResponse',
            '401': None,
            '403': None,
            '404': None,
            '500': 'ManifestErrorsResponse',
        }
        response_data = self.api_client.call_api(*_param, _request_timeout=_request_timeout)
        return response_data.response

    def _retry_manifest_async_serialize(
        self,
        manifest_identifier,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:
        _auth_settings, _body_params, _collection_formats, _files, _form_params, _header_params, _host, _path_params, _query_params = self.manifest_get_2(
            _headers,
            manifest_identifier
        )

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/manifests/retry/{manifestIdentifier}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )


