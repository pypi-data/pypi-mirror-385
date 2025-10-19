import logging
import uuid
import base64
import httpx

from ..core import Thing, Action
from ..core.zmq import SyncZMQClient, AsyncZMQClient
from ..td.interaction_affordance import (
    PropertyAffordance,
    ActionAffordance,
    EventAffordance,
)
from ..serializers import Serializers
from ..utils import get_default_logger, set_global_event_loop_policy
from ..constants import ZMQ_TRANSPORTS
from .abstractions import ConsumedThingAction, ConsumedThingProperty, ConsumedThingEvent
from .proxy import ObjectProxy
from .http.consumed_interactions import HTTPProperty, HTTPAction, HTTPEvent
from .zmq.consumed_interactions import (
    ZMQAction,
    ZMQEvent,
    ZMQProperty,
    WriteMultipleProperties,
    ReadMultipleProperties,
)


set_global_event_loop_policy()


class ClientFactory:
    """
    An factory class for creating clients to interact with Things over different protocols.
    This object is not meant to be instantiated, but rather to provide class methods for creating clients.
    """

    __wrapper_assignments__ = ("__name__", "__qualname__", "__doc__")

    @classmethod
    def zmq(
        self,
        server_id: str,
        thing_id: str,
        access_point: str = ZMQ_TRANSPORTS.IPC,
        **kwargs,
    ) -> ObjectProxy:
        """
        Create a ZMQ client for the specified server and thing.

        Parameters
        ----------
        server_id: str
            The ID of the server to connect to
        thing_id: str
            The ID of the thing to interact with
        access_point: str
            The ZMQ protocol to use for communication (`IPC` or `INPROC`) or `tcp://<host>:<port>` for TCP
        kwargs:
            Additional configuration options:

            - `logger`: `logging.Logger`, optional.
                 A custom logger instance to use for logging
            - `log_level`: `int`, default `logging.INFO`.
                The logging level to use for the client (e.g., logging.DEBUG, logging.INFO)
            - `ignore_TD_errors`: `bool`, default `False`.
                Whether to ignore errors while fetching the Thing Description (TD)
            - `skip_interaction_affordances`: `list[str]`, default `[]`.
                A list of interaction names to skip (property, action or event names)
            - `invokation_timeout`: `float`, optional, default `5.0`.
                The timeout for invokation requests (in seconds)
            - `execution_timeout`: `float`, optional, default `5.0`.
                The timeout for execution requests (in seconds)

        Returns
        -------
        ObjectProxy
            An ObjectProxy instance representing the remote Thing
        """
        id = f"{server_id}|{thing_id}|{access_point}|{uuid.uuid4()}"

        # configs
        ignore_TD_errors = kwargs.get("ignore_TD_errors", False)
        skip_interaction_affordances = kwargs.get("skip_interaction_affordances", [])
        invokation_timeout = kwargs.get("invokation_timeout", 5.0)
        execution_timeout = kwargs.get("execution_timeout", 5.0)
        logger = kwargs.get("logger", get_default_logger(id, log_level=kwargs.get("log_level", logging.INFO)))

        # ZMQ req-rep clients
        sync_zmq_client = SyncZMQClient(f"{id}|sync", server_id=server_id, logger=logger, access_point=access_point)
        async_zmq_client = AsyncZMQClient(f"{id}|async", server_id=server_id, logger=logger, access_point=access_point)

        # Fetch the TD
        assert isinstance(Thing.get_thing_model, Action)
        FetchTDAffordance = Thing.get_thing_model.to_affordance()
        FetchTDAffordance.override_defaults(name="get_thing_description", thing_id=thing_id)
        FetchTD = ZMQAction(
            resource=FetchTDAffordance,
            sync_client=sync_zmq_client,
            async_client=async_zmq_client,
            invokation_timeout=invokation_timeout,
            execution_timeout=execution_timeout,
            owner_inst=None,
            logger=logger,
        )
        TD = FetchTD(
            ignore_errors=ignore_TD_errors,
            protocol=access_point.split("://")[0].upper() if access_point else "IPC",
            skip_names=skip_interaction_affordances,
        )  # typing.Dict[str, typing.Any]

        # create ObjectProxy
        object_proxy = ObjectProxy(
            id=id,
            td=TD,
            logger=logger,
            invokation_timeout=invokation_timeout,
            execution_timeout=execution_timeout,
        )

        # add properties
        for name in TD.get("properties", []):
            affordance = PropertyAffordance.from_TD(name, TD)
            consumed_property = ZMQProperty(
                resource=affordance,
                sync_client=sync_zmq_client,
                async_client=async_zmq_client,
                owner_inst=object_proxy,
                invokation_timeout=invokation_timeout,
                execution_timeout=execution_timeout,
                logger=logger,
            )
            self.add_property(object_proxy, consumed_property)
            if hasattr(affordance, "observable") and affordance.observable:
                consumed_observable = ZMQEvent(
                    resource=affordance,
                    owner_inst=object_proxy,
                    logger=logger,
                )
                self.add_event(object_proxy, consumed_observable)
        # add actions
        for action in TD.get("actions", []):
            affordance = ActionAffordance.from_TD(action, TD)
            consumed_action = ZMQAction(
                resource=affordance,
                sync_client=sync_zmq_client,
                async_client=async_zmq_client,
                owner_inst=object_proxy,
                invokation_timeout=invokation_timeout,
                execution_timeout=execution_timeout,
                logger=logger,
            )
            self.add_action(object_proxy, consumed_action)
        # add events
        for event in TD.get("events", []):
            affordance = EventAffordance.from_TD(event, TD)
            consumed_event = ZMQEvent(
                resource=affordance,
                owner_inst=object_proxy,
                logger=logger,
            )
            self.add_event(object_proxy, consumed_event)
        # add top level form handlers (for ZMQ even if said form exists or not)
        for opname, ophandler in zip(
            ["_get_properties", "_set_properties"],
            [ReadMultipleProperties, WriteMultipleProperties],
        ):
            setattr(
                object_proxy,
                opname,
                ophandler(
                    sync_client=sync_zmq_client,
                    async_client=async_zmq_client,
                    owner_inst=object_proxy,
                    invokation_timeout=invokation_timeout,
                    execution_timeout=execution_timeout,
                    logger=logger,
                ),
            )
        return object_proxy

    @classmethod
    def http(self, url: str, **kwargs) -> ObjectProxy:
        """
        Create a HTTP client using the Thing Description (TD) available at the specified URL.

        Parameters
        ----------
        url: str
            The URL of the Thing Description (TD) to fetch.
        kwargs:
            Additional configuration options:

            - `logger`: `logging.Logger`, optional.
                A custom logger instance to use for logging
            - `log_level`: `int`, default `logging.INFO`.
                The logging level to use for the client (e.g., logging.DEBUG, logging.INFO)
            - `ignore_TD_errors`: `bool`, default `False`.
                Whether to ignore errors while fetching the Thing Description (TD)
            - `skip_interaction_affordances`: `list[str]`, default `[]`.
                A list of interaction names to skip (property, action or event names)
            - `invokation_timeout`: `float`, optional, default `5.0`.
                The timeout for operation invokation (in seconds)
            - `execution_timeout`: `float`, optional, default `5.0`.
                The timeout for operation execution (in seconds)
            - `connect_timeout`: `float`, optional, default `10.0`.
                The timeout for establishing a HTTP connection (in seconds)
            - `request_timeout`: `float`, optional, default `60.0`.
                The timeout for completing a HTTP request (in seconds)
            - `username`: `str`, optional.
                The username for HTTP Basic Authentication
            - `password`: `str`, optional.
                The password for HTTP Basic Authentication

        Returns
        -------
        ObjectProxy
            An ObjectProxy instance representing the remote Thing
        """

        # config
        skip_interaction_affordances = kwargs.get("skip_interaction_affordances", [])
        invokation_timeout = kwargs.get("invokation_timeout", 5.0)
        execution_timeout = kwargs.get("execution_timeout", 5.0)
        connect_timeout = kwargs.get("connect_timeout", 10.0)
        request_timeout = kwargs.get("request_timeout", 60.0)
        use_localhost = False
        if (
            "http://localhost" in url
            or "http://localhost" in url
            or "http://[::1]" in url
            or "http://[::1]" in url
            or "http://127.0.0.1" in url
        ):
            use_localhost = True

        # create clients
        req_rep_timeout = httpx.Timeout(
            connect=connect_timeout,
            read=request_timeout,
            write=request_timeout,
            pool=2,
        )
        sse_timeout = httpx.Timeout(
            connect=connect_timeout,
            read=3,
            write=request_timeout,
            pool=2,
        )

        req_rep_sync_client = httpx.Client(timeout=req_rep_timeout)
        req_rep_async_client = httpx.AsyncClient(timeout=req_rep_timeout)
        sse_sync_client = httpx.Client(timeout=sse_timeout)
        sse_async_client = httpx.AsyncClient(timeout=sse_timeout)

        # fetch TD
        url = (
            f"{url}?"
            + f"ignore_errors={str(kwargs.get('ignore_TD_errors', False)).lower()}"
            + (f"&skip_names={','.join(skip_interaction_affordances)}" if skip_interaction_affordances else "")
            + f"&use_localhost={str(use_localhost).lower()}"
        )

        # fetch TD
        headers = {"Content-Type": "application/json"}
        username = kwargs.get("username")
        password = kwargs.get("password")
        if username and password:
            token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
            headers["Authorization"] = f"Basic {token}"

        response = req_rep_sync_client.get(url, headers=headers)  # type: httpx.Response
        response.raise_for_status()

        TD = Serializers.json.loads(response.content)
        id = f"client|{TD['id']}|HTTP|{uuid.uuid4().hex[:8]}"
        logger = kwargs.get("logger", get_default_logger(id, log_level=kwargs.get("log_level", logging.INFO)))
        object_proxy = ObjectProxy(id, td=TD, logger=logger, **kwargs)

        for name in TD.get("properties", []):
            affordance = PropertyAffordance.from_TD(name, TD)
            consumed_property = HTTPProperty(
                resource=affordance,
                sync_client=req_rep_sync_client,
                async_client=req_rep_async_client,
                invokation_timeout=invokation_timeout,
                execution_timeout=execution_timeout,
                owner_inst=object_proxy,
                logger=logger,
            )
            self.add_property(object_proxy, consumed_property)
            if affordance.observable:
                consumed_event = HTTPEvent(
                    resource=affordance,
                    sync_client=sse_sync_client,
                    async_client=sse_async_client,
                    invokation_timeout=invokation_timeout,
                    execution_timeout=execution_timeout,
                    owner_inst=object_proxy,
                    logger=logger,
                )
                self.add_event(object_proxy, consumed_event)
        for action in TD.get("actions", []):
            affordance = ActionAffordance.from_TD(action, TD)
            consumed_action = HTTPAction(
                resource=affordance,
                sync_client=req_rep_sync_client,
                async_client=req_rep_async_client,
                invokation_timeout=invokation_timeout,
                execution_timeout=execution_timeout,
                owner_inst=object_proxy,
                logger=logger,
            )
            self.add_action(object_proxy, consumed_action)
        for event in TD.get("events", []):
            affordance = EventAffordance.from_TD(event, TD)
            consumed_event = HTTPEvent(
                resource=affordance,
                sync_client=sse_sync_client,
                async_client=sse_async_client,
                invokation_timeout=invokation_timeout,
                execution_timeout=execution_timeout,
                owner_inst=object_proxy,
                logger=logger,
            )
            self.add_event(object_proxy, consumed_event)

        return object_proxy

    @classmethod
    def add_action(self, client, action: ConsumedThingAction) -> None:
        # if not func_info.top_owner:
        #     return
        #     raise RuntimeError("logic error")
        # for dunder in ClientFactory.__wrapper_assignments__:
        #     if dunder == '__qualname__':
        #         info = '{}.{}'.format(client.__class__.__name__, func_info.get_dunder_attr(dunder).split('.')[1])
        #     else:
        #         info = func_info.get_dunder_attr(dunder)
        #     setattr(action, dunder, info)
        setattr(client, action.resource.name, action)

    @classmethod
    def add_property(self, client, property: ConsumedThingProperty) -> None:
        # if not property_info.top_owner:
        #     return
        #     raise RuntimeError("logic error")
        # for attr in ['__doc__', '__name__']:
        #     # just to imitate _add_method logic
        #     setattr(property, attr, property_info.get_dunder_attr(attr))
        setattr(client, property.resource.name, property)

    @classmethod
    def add_event(cls, client, event: ConsumedThingEvent) -> None:
        if hasattr(event.resource, "observable") and event.resource.observable:
            setattr(client, f"{event.resource.name}_change_event", event)
        else:
            setattr(client, event.resource.name, event)
