"""
Pydantic models for deserialising and normalising MBTA V3 API responses.

Each class corresponds to one MBTA V3 resource type and extends
:class:`FetchAttribute`, which wires up a three-step fetch-and-parse
lifecycle:

1. :meth:`FetchAttribute.api` calls :class:`~api_main.MbtaApi` to retrieve
   the raw JSON from the MBTA V3 API.
2. The abstract :meth:`FetchAttribute.from_api` method (implemented by each
   subclass) flattens the nested MBTA JSON:API structure into a plain list of
   ``dict`` objects whose keys match the model's Pydantic field names.
3. Pydantic's ``model_validate`` coerces each dict into a typed, validated
   model instance.

Currently implemented models:

* :class:`Lines` — transit line groupings (e.g. Red Line, Green Line).
* :class:`Route` — individual service routes within a line
  (e.g. Green-B, Green-C).
* :class:`Vehicles` — real-time vehicle positions and statuses.

Typical usage::

    from mbta.api.data_parsing import Vehicles

    vehicles = Vehicles.api()          # returns list[Vehicles]
    for v in vehicles:
        print(v.id, v.latitude, v.longitude)
"""

from abc import ABC, abstractmethod
from typing import Union

from pydantic import BaseModel

from src.mbta_app.mbta_connector.api_main import MbtaApi


class FetchAttribute(BaseModel, ABC):
    """
    Abstract base that combines Pydantic validation with MBTA API fetching.

    All MBTA resource models inherit from this class and gain a class-level
    :meth:`api` method that handles the full fetch → parse → validate
    pipeline.  Subclasses must implement :meth:`from_api` to define how the
    raw MBTA JSON structure is flattened into plain ``dict`` objects.

    Inheriting from both :class:`~pydantic.BaseModel` and
    :class:`~abc.ABC` ensures subclasses receive Pydantic field validation
    *and* are required to satisfy the :meth:`from_api` contract.

    .. note::
        The lowercased class name of each subclass is used as the ``attr``
        argument passed to :meth:`~api_main.MbtaApi.get_data`, so the name
        **must** match a member name of :class:`~utils.APICallSettings`.
    """

    @classmethod
    def api(cls) -> list:
        """
        Fetch, parse, and validate all records of this resource from the MBTA API.

        Orchestrates the full data-retrieval lifecycle:

        1. Instantiates :class:`~api_main.MbtaApi` and calls
           :meth:`~api_main.MbtaApi.get_data` using the lowercased class name
           as the attribute key.
        2. Passes the ``'data'`` list from the raw response to
           :meth:`from_api` for flattening.
        3. Runs each flattened dict through Pydantic's ``model_validate`` to
           produce typed, validated model instances.

        :returns: A list of fully-validated model instances for every record
            returned by the API.
        :rtype: list[Self]
        :raises ValueError: If the class name does not match a key in
            :class:`~utils.APICallSettings`, or if the HTTP request fails.
        :raises pydantic.ValidationError: If a field in any record cannot be
            coerced to its declared type.

        Example::

            lines = Lines.api()
            # [Lines(long_name='Blue Line', short_name='Blue', id='line-Blue'), ...]
        """
        api_obj: MbtaApi = MbtaApi()
        api_data: dict = api_obj.get_data(
            cls.__name__.lower()
        )
        cleaned_api_data: list = cls.from_api(
            api_data.get('data')
        )
        return [cls.model_validate(d)
                for d
                in cleaned_api_data]

    @classmethod
    @abstractmethod
    def from_api(cls, **kwargs):
        """
        Flatten the raw MBTA V3 ``'data'`` list into field-keyed dictionaries.

        Subclasses must override this method to extract the attributes and
        relationships they care about from the deeply-nested MBTA JSON:API
        structure, returning them as a flat list of ``dict`` objects whose
        keys correspond exactly to the model's Pydantic field names.

        :param kwargs: Concrete implementations receive the raw ``data`` list
            (a list of MBTA JSON:API resource objects) as a keyword argument
            named ``data``.
        :returns: A list of plain dictionaries, each representing one resource
            record with keys matching this model's field names.
        :rtype: list[dict]

        .. note::
            The abstract signature uses ``**kwargs`` to give subclasses
            flexibility in declaring their parameters.  Concrete
            implementations should use an explicit ``data: list`` parameter.
        """
        pass


class Lines(FetchAttribute):
    """
    Pydantic model representing a single MBTA transit *line*.

    A *line* in the MBTA V3 API is a named grouping of related routes
    (e.g. ``line-Red`` groups all Red Line routes).  This model captures the
    display-facing attributes most useful for a live map UI.

    :param long_name: Full human-readable name (e.g. ``'Red Line'``).
    :type long_name: str | int
    :param short_name: Abbreviated display name (e.g. ``'Red'``).  May be
        an integer for certain non-rail lines.
    :type short_name: str | int
    :param id: Unique MBTA V3 line identifier (e.g. ``'line-Red'``).
    :type id: str

    Example::

        lines = Lines.api()
        red = next(l for l in lines if l.id == 'line-Red')
        print(red.long_name)   # 'Red Line'
    """

    long_name: Union[str, int]
    short_name: Union[str, int]
    id: str

    @classmethod
    def from_api(cls, data: dict) -> list[dict]:
        """
        Flatten a raw MBTA V3 ``/lines`` data list into :class:`Lines`-compatible dicts.

        Extracts ``id`` from the top-level resource object and ``long_name``
        / ``short_name`` from the nested ``attributes`` dict.

        :param data: The list of JSON:API resource objects returned under the
            top-level ``'data'`` key of the ``/lines`` response.
        :type data: list[dict]
        :returns: A list of flattened dictionaries with keys ``id``,
            ``long_name``, and ``short_name``.
        :rtype: list[dict]
        """
        cleaned_data: list = []
        for _d in data:
            cleaned_data.append(
                {
                    'id': _d.get('id'),
                    'long_name': _d.get('attributes').get('long_name'),
                    'short_name': _d.get('attributes').get('short_name'),
                }
            )
        return cleaned_data


class Route(FetchAttribute):
    """
    Pydantic model representing a single MBTA transit *route*.

    A *route* is a specific service pattern within a :class:`Lines` line.
    For example, the Green Line has four routes: Green-B, Green-C, Green-D,
    and Green-E.  This model captures both the route's own attributes and
    its relationship back to the parent line.

    :param long_name: Full human-readable route name.
    :type long_name: str | int
    :param short_name: Abbreviated display name.
    :type short_name: str | int
    :param id: Unique MBTA V3 route identifier (e.g. ``'Green-B'``).
    :type id: str
    :param description: Plain-text description of the route type or service.
    :type description: str
    :param direction_destinations: Two-element list naming the terminal stops
        for each direction (index 0 = direction 0, index 1 = direction 1).
    :type direction_destinations: list
    :param fare_class: Fare category string (e.g. ``'Rapid Transit'``).
    :type fare_class: str
    :param relationships: Full ``relationships`` dict from the MBTA JSON:API
        response, kept for downstream use.
    :type relationships: dict
    :param line: Parent line identifier extracted from
        ``relationships → line → data → id`` (e.g. ``'line-Green'``).
    :type line: str
    """

    long_name: Union[str, int]
    short_name: Union[str, int]
    id: str
    description: str
    direction_destinations: list
    fare_class: str
    relationships: dict
    line: str

    @classmethod
    def from_api(cls, data: dict) -> list[dict]:
        """
        Flatten a raw MBTA V3 ``/routes`` data list into :class:`Route`-compatible dicts.

        Extracts scalar attributes from ``attributes``, retains the full
        ``relationships`` dict, and navigates
        ``relationships → line → data → id`` to surface the parent line
        identifier as a top-level field.

        :param data: The list of JSON:API resource objects returned under the
            top-level ``'data'`` key of the ``/routes`` response.
        :type data: list[dict]
        :returns: A list of flattened dictionaries with keys matching every
            field declared on :class:`Route`.
        :rtype: list[dict]
        :raises AttributeError: If the ``relationships.line.data`` path is
            absent from any record, indicating an unexpected API schema change.
        """
        cleaned_data: list = []
        for _d in data:
            cleaned_data.append(
                {
                    'id': _d.get('id'),
                    'description': _d.get('attributes').get('description'),
                    'direction_destinations': _d.get('attributes').get('direction_destinations'),
                    'fare_class': _d.get('attributes').get('fare_class'),
                    'long_name': _d.get('attributes').get('long_name'),
                    'short_name': _d.get('attributes').get('short_name'),
                    'relationships': _d.get('relationships'),
                    'line': _d.get('relationships').get('line').get('data').get('id'),
                }
            )
        return cleaned_data


class Vehicles(FetchAttribute):
    """
    Pydantic model representing the real-time state of a single MBTA vehicle.

    Vehicles are the primary data source for the live map feature.  Each
    instance captures a vehicle's current geographic position, operational
    status, and its relationships to a route and trip.

    :param id: Unique vehicle identifier (e.g. ``'y1793'``).
    :type id: str | int
    :param current_status: MBTA movement status — one of
        ``'IN_TRANSIT_TO'``, ``'STOPPED_AT'``, or ``'INCOMING_AT'``.
    :type current_status: str | int
    :param current_stop_sequence: Stop-sequence number for the vehicle's
        current or upcoming stop.  ``None`` if not yet assigned.
    :type current_stop_sequence: str | int | None
    :param direction_id: Travel direction (``0`` or ``1``), corresponding to
        the indices of :attr:`Route.direction_destinations`.
    :type direction_id: int | None
    :param latitude: Current WGS-84 latitude of the vehicle.
    :type latitude: str | int | float
    :param longitude: Current WGS-84 longitude of the vehicle.
    :type longitude: str | int | float
    :param updated_at: ISO 8601 timestamp of the most recent position update.
    :type updated_at: str
    :param relationships: Full ``relationships`` dict from the MBTA JSON:API
        response, kept for downstream use.
    :type relationships: dict
    :param route: Parent route identifier extracted from
        ``relationships → route → data → id`` (e.g. ``'Red'``).
    :type route: str | int
    :param trip: Active trip identifier extracted from
        ``relationships → trip → data → id``.
    :type trip: str | int

    Example::

        vehicles = Vehicles.api()
        for v in vehicles:
            print(f"{v.id}: ({v.latitude}, {v.longitude}) on {v.route}")
    """

    id: Union[str, int]
    current_status: Union[str, int]
    current_stop_sequence: Union[str,int,None]
    direction_id: Union[None,int]
    latitude: Union[str,int,float]
    longitude: Union[str,int,float]
    updated_at: str
    relationships: dict
    route: Union[str, int]
    trip: Union[str, int]

    @classmethod
    def from_api(cls, data: dict) -> list[dict]:
        """
        Flatten a raw MBTA V3 ``/vehicles`` data list into :class:`Vehicles`-compatible dicts.

        Extracts all positional and status attributes from ``attributes``,
        retains the full ``relationships`` dict, and surfaces both the route
        and trip identifiers as top-level fields by navigating
        ``relationships → route/trip → data → id``.

        :param data: The list of JSON:API resource objects returned under the
            top-level ``'data'`` key of the ``/vehicles`` response.
        :type data: list[dict]
        :returns: A list of flattened dictionaries with keys matching every
            field declared on :class:`Vehicles`.
        :rtype: list[dict]
        :raises AttributeError: If either ``relationships.route.data`` or
            ``relationships.trip.data`` is absent from any record, indicating
            an unexpected API schema change or an unassigned vehicle.
        """
        cleaned_data: list = []
        for _d in data:
            cleaned_data.append(
                {
                    'id': _d.get('id'),
                    'current_status': _d.get('attributes').get('current_status'),
                    'current_stop_sequence': _d.get('attributes').get('current_stop_sequence'),
                    'direction_id': _d.get('attributes').get('direction_id'),
                    'latitude': _d.get('attributes').get('latitude'),
                    'longitude': _d.get('attributes').get('longitude'),
                    'updated_at': _d.get('attributes').get('updated_at'),
                    'relationships': _d.get('relationships'),
                    'route': _d.get('relationships').get('route').get('data').get('id'),
                    'trip': _d.get('relationships').get('trip').get('data').get('id')
                }
            )
        return cleaned_data