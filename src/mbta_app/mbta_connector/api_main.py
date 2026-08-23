"""
High-level MBTA V3 REST API client.

This module holds :class:`MbtaApi`, the single entry-point for making
data requests to the MBTA V3 API.  It delegates all HTTP
handling to :mod:`mbta.api.utils`, and validates
caller-supplied attribute names before issuing any request.

Example::

    from mbta.api.api_main import MbtaApi

    api = MbtaApi()
    response = api.get_data('vehicles')
    # response is a dict with a top-level 'data' key containing a list of vehicle resource objects.
"""

from src.mbta_app.mbta_connector.utils import APISettings, validate, fetch_json, APICallSettings


class MbtaApi:
    """
    Client / connection for the MBTA V3 REST API.

    On instantiation the client reads its ``web_address`` and ``api_key``
    from :class:`~utils.APISettings`.  Callers then use :meth:`get_data`
    to retrieve any supported resource type.

    :ivar web_address: Base URL template
        (``https://api-v3.mbta.com/{attribute_param}``).
    :vartype web_address: str
    :ivar api_key: MBTA V3 API key sourced from Windows Credential Manager.
    :vartype api_key: str

    Examples::

        api = MbtaApi()
        vehicles = api.get_data('vehicles')
        routes   = api.get_data('route')
    """

    def __init__(self) -> None:
        """
        Initialise the API client with settings from :class:`~utils.APISettings`.

        No direct connection is performed during initialisation. The API key is
        read from Windows Credential Manager once at *module import* time
        inside :class:`~utils.APISettings`, not on each client construction.
        """
        self.web_address: str = APISettings.WEB_ADDRESS
        self.api_key: str = APISettings.API_KEY

    def _get_data(self, attribute_param: str) -> dict:
        """
        Builds the request URL and delegates to
        :func:`~utils.fetch_json`.

        Formats :attr:`web_address` with *attribute_param* and issues the HTTP
        GET via :func:`~utils.fetch_json`. This method is intentionally
        private; callers should always go through :meth:`get_data`, which
        validates the attribute name before reaching here.

        :param attribute_param: The MBTA V3 URL path segment (e.g.
            ``'vehicles'``, ``'routes'``).  This is the *value* of a
            :class:`~utils.APICallSettings` member, not the member name.
        :type attribute_param: str
        :returns: The raw JSON-decoded response body from the MBTA V3 API.
        :rtype: dict
        :raises ValueError: Propagated from :func:`~utils.fetch_json` on
            non-200 HTTP responses.
        """
        _response: dict = fetch_json(
            self.web_address.format(
                attribute_param=attribute_param
            )
            ,api_key=self.api_key
        )
        return _response

    def get_data(self, attr: str) -> dict:
        """
        Validate *attr* and return the MBTA V3 JSON response for that resource.

        This is the primary public interface of :class:`MbtaApi`.  It
        validates the caller-supplied attribute name against
        :class:`~utils.APICallSettings`, resolves the corresponding URL path
        segment, then delegates the HTTP request to :meth:`_get_data`.

        :param attr: A recognised MBTA attribute name — must match one of the
            *member names* of :class:`~utils.APICallSettings`, e.g.
            ``'vehicles'``, ``'route'``, or ``'lines'``.
        :type attr: str
        :returns: The JSON-decoded API response. The MBTA V3 API wraps
            resource collections under a top-level ``'data'`` key.
        :rtype: dict
        :raises ValueError: If *attr* is not a recognised member of
            :class:`~utils.APICallSettings` (raised by
            :func:`~utils.validate`).
        :raises ValueError: If the underlying HTTP request returns a non-200
            status code (raised by :func:`~utils.fetch_json`).

        Examples::
            api = MbtaApi()
            data = api.get_data('vehicles')
            for vehicle in data['data']:
                print(vehicle['id'], vehicle['attributes']['latitude'])
        """
        validate(attr)
        return self._get_data(
            APICallSettings.__getitem__(attr).value
        )