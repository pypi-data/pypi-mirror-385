from __future__ import annotations

import asyncio
import functools
import inspect
import signal
from asyncio import Event, Queue
from datetime import timedelta
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

from pydantic import Field
from pydantic.dataclasses import dataclass
from typing_extensions import Literal, ParamSpec, Self, TypeGuard

from kelvin.application import filters
from kelvin.application.stream import KelvinStream, KelvinStreamConfig
from kelvin.application.timer import Timer
from kelvin.krn import KRNAsset, KRNAssetDataStream
from kelvin.logs import configure_logger, logger
from kelvin.message import AssetDataMessage, ControlChangeStatus, KMessageType, KMessageTypeData, Message
from kelvin.message.base_messages import ParameterType, PropertyType
from kelvin.message.msg_builders import CustomAction, MessageBuilder, convert_message
from kelvin.message.runtime_manifest import ManifestDatastream, Resource, RuntimeManifest, WayEnum

if TYPE_CHECKING:
    from kelvin.application.window import HoppingWindow, RollingWindow, TumblingWindow

E = TypeVar("E", bound=Exception)
T = TypeVar("T", bound=Message)

# Task Types
P = ParamSpec("P")
R = TypeVar("R")

SyncFunc = Callable[P, R]
AsyncFunc = Callable[P, Awaitable[R]]
TaskFunc = Union[SyncFunc[P, R], AsyncFunc[P, R]]


# Stream Types
StreamSyncFunc = Callable[[AssetDataMessage], Any]
StreamAsyncFunc = Callable[[AssetDataMessage], Awaitable[Any]]
StreamFunc = Union[StreamSyncFunc, StreamAsyncFunc]


@dataclass
class Datastream:
    name: str
    type: KMessageType
    unit: Optional[str] = None


class AppIO(Datastream):
    pass


@dataclass
class ResourceDatastream:
    asset: KRNAsset
    io_name: str
    datastream: Datastream
    configuration: Dict = Field(default_factory=dict)
    way: WayEnum = WayEnum.output

    # deprecated
    owned: bool = False
    access: Literal["RO", "RW", "WO"] = "RO"


@dataclass
class AssetInfo:
    name: str
    properties: Dict[str, PropertyType] = Field(default_factory=dict)
    parameters: Dict[str, ParameterType] = Field(default_factory=dict)
    datastreams: Dict[str, ResourceDatastream] = Field(default_factory=dict)


class KelvinApp:
    """
    Kelvin App to connect and interface with the KelvinStream.

    After connecting, the connection is handled automatically in the background.

    Use filters or filter_stream to easily listen for specific messages.
    Use register_callback methods to register callbacks for events like connect and disconnect.
    Use tasks to run background functions that can be async or sync.
    Use timers to run functions at regular intervals.

    The app can be used as an async context manager, which will automatically connect on enter and disconnect on exit.

    Example usage:
        async with KelvinApp() as app:
            await app.publish(Number(resource=KRNAssetDataStream('my-asset', 'my-input'), payload=1.0))
            async for msg in app.stream_filter(filters.is_asset_data_message):
                print(msg)

    """

    _MAX_BACKOFF = 60

    def __init__(self, config: KelvinStreamConfig = KelvinStreamConfig()) -> None:
        self._stream = KelvinStream(config)

        # App Filters
        self._filters: List[Tuple[Queue, Callable[[Message], TypeGuard[Message]]]] = []

        # App Configuration
        self._app_configuration: dict = {}

        # App Assets
        self._assets: Dict[str, AssetInfo] = {}

        # App IO
        self._inputs: List[AppIO] = []
        self._outputs: List[AppIO] = []

        # App Tasks
        self._tasks: Dict[str, AsyncFunc] = {}
        self._running_tasks: Set[asyncio.Task[Any]] = set()

        # App Internal State
        self._connect_lock = asyncio.Lock()
        self._read_loop_task: Optional[asyncio.Task[Any]] = None
        self._config_received: Event = Event()

        # App Runtime Manifest
        self._runtime_manifest: Optional[RuntimeManifest] = None

        # App Callbacks
        self.on_connect: Optional[Callable[[], Awaitable[None]]] = None
        """Called when the connection is established."""

        self.on_disconnect: Optional[Callable[[], Awaitable[None]]] = None
        """Called when the connection is closed."""

        self.on_message: Optional[Callable[[Message], Awaitable[None]]] = None
        """Called on receipt of any message."""

        self.on_asset_input: Optional[Callable[[AssetDataMessage], Awaitable[None]]] = None
        """Called when an asset data message is received."""

        self.on_control_change: Optional[Callable[[AssetDataMessage], Awaitable[None]]] = None
        """Called when a control change message is received."""

        self.on_control_status: Optional[Callable[[ControlChangeStatus], Awaitable[None]]] = None
        """Called when a control status is received."""

        self.on_custom_action: Optional[Callable[[CustomAction], Awaitable[None]]] = None
        """Called when a custom action is received."""

        self.on_asset_change: Optional[Callable[[Optional[AssetInfo], Optional[AssetInfo]], Awaitable[None]]] = None
        """Called when an asset is added, removed, or modified.
        First arg is the new asset (None if removed); second is the previous asset (None if newly added)."""

        self.on_app_configuration: Optional[Callable[[dict], Awaitable[None]]] = None
        """Called when the app configuration changes."""

        configure_logger()

    # ----------------
    # Properties
    # ----------------
    @property
    def is_connected(self) -> bool:
        """
        Indicates whether the read loop is active, implying an established connection.
        """
        return bool(self._read_loop_task and not self._read_loop_task.done())

    @property
    def assets(self) -> Dict[str, AssetInfo]:
        """
        Get all assets configured for this application.

        It returns a dictionary where each key is the asset name, and the value is an `AssetInfo` object
        describing that asset's properties, parameters, and datastreams.

        The `assets` dictionary is dynamically updated whenever the application receives
        updates to asset properties or parameters, ensuring it always reflects the latest configuration.

        Returns:
            Dict[str,AssetInfo]: A dictionary where keys are asset names (strings) and values are AssetInfo instances
                representing the current configuration and state of each asset.

        Example:
            {
                "asset1": AssetInfo(
                    name="asset1",
                    properties={
                        "tubing_length": 25.0,
                        "area": 11.0
                    },
                    parameters={
                        "param-bool": False,
                        "param-number": 7.5,
                        "param-string": "hello"
                    },
                    datastreams={
                        "output1": ResourceDatastream(
                            asset=KRNAsset("asset1"),
                            io_name="output1",
                            datastream=Datastream(
                                name="datastream1",
                                type=KMessageTypeData("float"),
                                unit="m"
                            ),
                            access="RO",
                            owned=True,
                            configuration={}
                        )
                    }
                )
            }
        """
        if not self.is_connected:
            raise RuntimeError("Cannot get assets: KelvinApp is not connected")

        return self._assets.copy()

    @property
    def app_configuration(self) -> dict:
        """
        Get the application configuration.

        Returns:
            dict: A mapping of configuration sections to their values, matching the structure in app.yaml.

        Example:
            {
                "foo": {
                    "conf_string": "value1",
                    "conf_number": 25,
                    "conf_bool": False,
                }
            }
        """

        if not self.is_connected:
            raise RuntimeError("Cannot get app_configuration: KelvinApp is not connected")

        return self._app_configuration

    @property
    def config_received(self) -> Event:
        """
        Event set when the initial configuration is received.

        Use this asyncio.Event to wait until the application has loaded its initial app/asset parameters.

        Returns:
            asyncio.Event: Event that becomes set once the initial configuration arrives.

        Example:
            await app.config_received.wait()
        """
        return self._config_received

    @property
    def inputs(self) -> List[AppIO]:
        """
        List all input metrics configured for the application.

        Each AppIO has:
            - name (str): the metric identifier.
            - data_type (str): the data type of the input.

        Returns:
            List[AppIO]: Read-only list of configured input metrics.
        """

        if not self.is_connected:
            raise RuntimeError("Cannot get inputs: KelvinApp is not connected")

        return self._inputs

    @property
    def outputs(self) -> List[AppIO]:
        """
        List all output metrics configured for the application.

        Each AppIO has:
            - name (str): the metric identifier.
            - data_type (str): the data type of the output.

        Returns:
            List[AppIO]: Read-only list of configured output metrics.
        """

        if not self.is_connected:
            raise RuntimeError("Cannot get outputs: KelvinApp is not connected")

        return self._outputs

    @property
    def tasks(self) -> Dict[str, Callable[[], Awaitable]]:
        """
        Retrieve registered asynchronous tasks.

        Returns:
            Dict[str, Callable[[], Awaitable]]: Dict of task names and callable that produce awaitables when called.
            Represents tasks scheduled or pending.
        """
        return self._tasks

    # ----------------
    # Async context‐manager support
    # ----------------
    async def __aenter__(self) -> Self:
        """
        Support async context: connect on enter.
        """
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[E]],
        exc_value: Optional[E],
        tb: Optional[TracebackType],
    ) -> Optional[bool]:
        """
        Support async context: disconnect on exit.
        """
        await self.disconnect()
        # Do not suppress exceptions
        return False

    # ----------------
    # Internal Helpers
    # ----------------
    async def _callback(self, callback: Optional[Callable[..., Awaitable[Any]]], *args: Any) -> None:
        """
        Safely invoke an async callback, catching and logging any exceptions (but allow cancellation to propagate).
        """
        if not callback:
            return

        try:
            await callback(*args)
        except asyncio.CancelledError:
            raise  # Propagate cancellation
        except Exception as ex:
            logger.exception("Error invoking callback", callback_name=callback.__name__, ex=ex)
            raise

    def _default_assets_and_datastreams(
        self, assets: Optional[List[str]] = None, datastreams: Optional[List[str]] = None
    ) -> Tuple[List[str], List[str]]:
        if not assets:
            assets = list(self.assets.keys())

        if not datastreams:
            datastreams = [ds.name for ds in self.inputs]

        return assets, datastreams

    def _apply_asset_datastream_filters(self, assets: List[str], datastreams: List[str]) -> Queue[AssetDataMessage]:
        def checker(msg: Message) -> TypeGuard[AssetDataMessage]:
            return filters.asset_equals(assets)(msg) and filters.input_equals(datastreams)(msg)

        return self.filter(checker)

    # ----------------
    # Connection Handling
    # ----------------
    async def connect(self) -> None:
        """
        Establish connection, retrying indefinitely until success.
        Starts the read loop and waits for App Configuration before firing `on_connect` callback and tasks/timers.
        """
        async with self._connect_lock:
            # Prevent duplicate connects
            if self.is_connected:
                return

            # Reset and start read loop
            self._config_received.clear()
            self._read_loop_task = asyncio.create_task(self._read_loop(), name="app-internal:read-loop")

            # Wait for the App Configuration before firing on_connect callback
            await self._config_received.wait()

            # Invoke on_connect callback
            await self._callback(self.on_connect)

            # Start all registered tasks
            await self._start_tasks()

    async def disconnect(self) -> None:
        """
        Cancel read loop, stop all tasks, fire on_disconnect, and close stream.
        """
        logger.debug("Disconnecting from KelvinStream...")

        async with self._connect_lock:
            # Cancel the read loop task
            await self._cancel_task(self._read_loop_task)
            self._read_loop_task = None

            # Cancel all background tasks
            await self._stop_tasks()

            # Disconnect from stream
            try:
                await self._stream.disconnect()
            except ConnectionError:
                pass

            # Invoke on_disconnect callback
            await self._callback(self.on_disconnect)

        logger.debug("Disconnected from KelvinStream")

    async def _retry_connect(self) -> None:
        """
        Keep calling stream.connect() with exponential backoff until success.
        """
        delay = 1
        while True:
            try:
                logger.debug("Connecting to KelvinStream...")
                await self._stream.connect()
                logger.debug("Successfully connected to KelvinStream")
                return
            except asyncio.CancelledError:
                raise
            except ConnectionError:
                logger.error(f"Connection to KelvinStream failed, retrying in {delay}s...")
                await asyncio.sleep(delay)
                delay = min(delay * 2, self._MAX_BACKOFF)

    async def _read_loop(self) -> None:
        """
        Persistent read loop: ensures connection, reads messages,
        triggers callbacks, and reconnects on error.
        """
        logger.debug("Read Loop: starting...")

        try:
            while True:
                await self._retry_connect()
                try:
                    while True:
                        msg = await self._stream.read()

                        await self._process_message(msg)

                        self._route_to_filters(msg)
                except asyncio.CancelledError:
                    return
                except ConnectionError:
                    logger.error("Read Loop: lost connection to KelvinStream, reconnecting...")
                except Exception as ex:
                    logger.error("Read Loop: unexpected error", ex=ex)
        finally:
            logger.debug("Read Loop: exiting")

    # ----------------
    # Message Handling
    # ----------------
    async def _process_app_configuration(self, configuration: Dict) -> None:
        if configuration != self.app_configuration:
            self._app_configuration = configuration

            # Invoke callback if it's not initial configuration
            if self._config_received.is_set():
                await self._callback(self.on_app_configuration, self.app_configuration)

    async def _process_resources(
        self,
        resources: List[Resource],
        datastreams: List[ManifestDatastream],
    ) -> None:
        """
        Synchronize self._assets, self._inputs, self._outputs based on the incoming
        resources list and the manifest datastream definitions; fire on_asset_change
        callbacks for any added, updated, or removed assets, but only once at the end.
        """
        # 1) Build manifest lookup
        manifest_ds_map: Dict[str, ManifestDatastream] = {ds.name: ds for ds in datastreams}

        # 2) Filter only real assets and warn on non-assets
        asset_resources: Dict[str, Resource] = {}
        for res in resources:
            if isinstance(res.resource, KRNAsset):
                asset_resources[res.resource.asset] = res
            else:
                logger.warning("Skipping non-asset resource %r", res.resource)

        # 3) Prepare new IO maps and collect change events
        new_inputs: Dict[str, AppIO] = {}
        new_outputs: Dict[str, AppIO] = {}

        # [(new_info, old_info), ...]
        callbacks: List[Tuple[Optional[AssetInfo], Optional[AssetInfo]]] = []

        # 4) Remember which assets existed before
        previous_assets = set(self._assets.keys())

        # 5) Process each current asset
        for asset_name, asset_cfg in asset_resources.items():
            new_info = AssetInfo(
                name=asset_name,
                properties=asset_cfg.properties,
                parameters=asset_cfg.parameters,
                datastreams={},
            )

            for ds_name, ds_cfg in asset_cfg.datastreams.items():
                manif_ds = manifest_ds_map.get(ds_name)
                if manif_ds is None:
                    logger.error("No manifest entry for datastream %s on asset %s", ds_name, asset_name)
                    continue

                io_name = ds_cfg.map_to or ds_name
                msg_type = KMessageTypeData(manif_ds.primitive_type_name)  # type: ignore

                new_info.datastreams[io_name] = ResourceDatastream(
                    asset=asset_cfg.resource,  # type: ignore
                    io_name=io_name,
                    access=ds_cfg.access,
                    way=ds_cfg.way,
                    owned=bool(ds_cfg.owned),
                    configuration=ds_cfg.configuration,
                    datastream=Datastream(name=ds_name, type=msg_type, unit=manif_ds.unit_name),
                )

                if ds_cfg.way in [WayEnum.input, WayEnum.input_output_cc]:
                    new_inputs[io_name] = AppIO(name=io_name, type=msg_type)
                elif ds_cfg.way in [WayEnum.output, WayEnum.input_cc_output]:
                    new_outputs[io_name] = AppIO(name=io_name, type=msg_type)

            # record change
            old_info: Optional[AssetInfo] = self._assets.get(asset_name)
            self._assets[asset_name] = new_info
            callbacks.append((new_info, old_info))

        # 6) Detect removed assets
        removed = previous_assets - set(asset_resources.keys())
        for name in removed:
            old_info_existing: AssetInfo = self._assets.pop(name)
            callbacks.append((None, old_info_existing))

        # 7) Update IO lists
        self._inputs = list(new_inputs.values())
        self._outputs = list(new_outputs.values())

        # 8) Invoke callback if it's not initial configuration
        if self._config_received.is_set():
            for new_info_opt, old_info_opt in callbacks:  # do not shadow the AssetInfo-typed new_info above
                await self._callback(self.on_asset_change, new_info_opt, old_info_opt)

    async def _process_runtime_manifest(self, msg: RuntimeManifest) -> None:
        logger.debug(f"Processing RuntimeManifest. Initial Manifest: {not self.config_received.is_set()}")

        await self._process_resources(msg.payload.resources, msg.payload.datastreams)
        await self._process_app_configuration(msg.payload.configuration)

        # Mark config received
        self._config_received.set()

    async def _process_message(self, msg: Message) -> None:
        """
        Route an incoming Message (or RuntimeManifest) to the proper async handler.
        """
        # Handle RuntimeManifest
        if isinstance(msg, RuntimeManifest):
            await self._process_runtime_manifest(msg)
            return

        # Invoke callbacks
        await self._callback(self.on_message, msg)

        if self.msg_is_control_change(msg):
            await self._callback(self.on_control_change, msg)
            return

        if filters.is_asset_data_message(msg):
            await self._callback(self.on_asset_input, msg)
            return

        if filters.is_control_status_message(msg):
            await self._callback(self.on_control_status, msg)
            return

        if filters.is_custom_action(msg):
            await self._callback(self.on_custom_action, convert_message(msg))  # type: ignore
            return

    def _route_to_filters(self, msg: Message) -> None:
        """
        Route a message to all registered filters.

        For each (queue, predicate) in self._filters:
          - If predicate(msg) returns True, convert the message if possible,
            then put it into the queue without waiting.
        """
        for queue, predicate in self._filters:
            try:
                if predicate(msg):
                    converted = convert_message(msg) or msg
                    # TODO: check if the message is reference
                    queue.put_nowait(converted)
            except Exception:
                # If a filter raises, we choose to ignore it or log if desired.
                logger.exception(f"Filter {predicate!r} raised on message: {msg!r}")

    # ----------------
    # Publish
    # ----------------
    async def publish(self, msg: Union[Message, MessageBuilder]) -> bool:
        """
        Publish a message to KelvinStream.

        Accepts either a Message instance or a MessageBuilder. If given a MessageBuilder,
        it is converted to a Message via `to_message()` before sending. Returns True on success,
        or False if the connection is unavailable.

        Args:
            msg (Union[Message, MessageBuilder]):
                - A Message to send directly, or
                - A MessageBuilder which will be converted to Message.

        Returns:
            bool:
                - True if the message was sent successfully.
                - False if sending failed due to a ConnectionError.

        Examples:
            message = Number(resource=KRNAssetDataStream('my-asset', 'my-input'), payload=1.0)
            success = await client.publish(message)
            if success:
                print("Published message")
            else:
                print("Publish failed")
        """

        if not self.is_connected:
            raise RuntimeError("Cannot publish message: App is not connected")

        try:
            if isinstance(msg, MessageBuilder):
                m = msg.to_message()
            else:
                m = msg

            return await self._stream.write(m)
        except ConnectionError:
            logger.error("Failed to publish message: Connection is unavailable")
            return False

    # ----------------
    # Filters
    # ----------------
    def filter(self, func: Callable[[Message], TypeGuard[T]]) -> Queue[T]:
        """
        Creates a filter for the received Kelvin Messages based on a filter function.

        Args:
            func (filters.KelvinFilterType): Filter function, it should receive a Message as argument and return bool.

        Returns:
            Queue[Message]: Returns a asyncio queue to receive the filtered messages.
        """
        queue: Queue[T] = Queue()
        self._filters.append((queue, func))
        return queue

    def stream_filter(self, func: Callable[[Message], TypeGuard[T]]) -> AsyncGenerator[T, None]:
        """
        Creates a stream for the received Kelvin Messages based on a filter function.
        See filter.

        Args:
            func (filters.KelvinFilterType): Filter function, it should receive a Message as argument and return bool.

        Returns:
            AsyncGenerator[Message, None]: Async Generator that can be async iterated to receive filtered messages.

        Yields:
            Iterator[AsyncGenerator[Message, None]]: Yields the filtered messages.
        """
        queue: Queue[T] = self.filter(func)

        async def _generator() -> AsyncGenerator[T, None]:
            while True:
                msg = await queue.get()
                yield msg

        return _generator()

    # ----------------
    # Windowing
    # ----------------
    def tumbling_window(
        self,
        window_size: timedelta,
        assets: Optional[List[str]] = None,
        inputs: Optional[List[str]] = None,
        round_to: Optional[timedelta] = None,
    ) -> TumblingWindow:
        """
        Creates a fixed, non-overlapping windowing.

        Args:
            window_size: Duration of each window.
            assets: Optional list of asset names to filter on.
            inputs: Optional list of input names (data streams) to include as columns in the window.
            round_to: Optional interval to which window boundaries are aligned.

        Returns:
            TumblingWindow: An instance configured with the given parameters.
        """

        from kelvin.application.window import TumblingWindow

        assets, inputs = self._default_assets_and_datastreams(assets, inputs)
        queue = self._apply_asset_datastream_filters(assets, inputs)

        return TumblingWindow(
            assets=assets,
            inputs=inputs,
            window_size=window_size,
            queue=queue,
            round_to=round_to,
        )

    def hopping_window(
        self,
        window_size: timedelta,
        hop_size: timedelta,
        assets: Optional[List[str]] = None,
        inputs: Optional[List[str]] = None,
        round_to: Optional[timedelta] = None,
    ) -> HoppingWindow:
        """
        Creates a window with fixed size and overlap.

        Args:
            window_size: Duration of each window.
            hop_size: Step between window starts (defines overlap).
            assets: Optional list of asset names to filter on.
            inputs: Optional list of input names (data streams) to include as columns in the window.
            round_to: Optional interval to which window boundaries are aligned.

        Returns:
            HoppingWindow: An instance configured with the given parameters.
        """
        from kelvin.application.window import HoppingWindow

        assets, inputs = self._default_assets_and_datastreams(assets, inputs)
        queue = self._apply_asset_datastream_filters(assets, inputs)

        return HoppingWindow(
            assets=assets,
            inputs=inputs,
            window_size=window_size,
            hop_size=hop_size,
            queue=queue,
            round_to=round_to,
        )

    def rolling_window(
        self,
        count_size: int,
        assets: Optional[List[str]] = None,
        inputs: Optional[List[str]] = None,
        round_to: Optional[timedelta] = None,
        slide: int = 1,
    ) -> RollingWindow:
        """
        Creates a sliding count-based window over incoming data.

        Args:
            count_size: Number of records per window.
            assets: Optional list of asset names to filter on.
            inputs: Optional list of input names (data streams) to include as columns in the window.
            round_to: Optional interval to which window boundaries are aligned.
            slide: Number of records to slide the window forward on each update.

        Returns:
            RollingWindow: An instance configured with the given parameters.
        """
        from kelvin.application.window import RollingWindow

        assets, inputs = self._default_assets_and_datastreams(assets, inputs)
        queue = self._apply_asset_datastream_filters(assets, inputs)

        return RollingWindow(
            assets=assets,
            inputs=inputs,
            count_size=count_size,
            queue=queue,
            round_to=round_to,
            slide=slide,
        )

    # ----------------
    # Stream
    # ----------------
    def stream(
        self,
        fn: Optional[StreamFunc] = None,
        *,
        assets: Optional[List[str]] = None,
        inputs: Optional[List[str]] = None,
    ) -> Union[AsyncFunc[P, R], Callable[[TaskFunc[P, R]], AsyncFunc[P, R]]]:
        """
        Register a per-message stream handler that is invoked for each incoming
        AssetDataMessage matching the optional assets/inputs filters.

        Usage patterns:

            @app.stream()
            async def my_stream(msg: AssetDataMessage): ...

            @app.stream(inputs=["in1"])
            async def my_stream(msg: AssetDataMessage): ...

            @app.stream(assets=["asset1"])
            async def my_stream(msg: AssetDataMessage): ...

            @app.stream(assets=["asset1"], inputs=["in1", "in2"])
            async def my_stream(msg: AssetDataMessage): ...

            @app.stream(assets=["asset1"], inputs=["in1", "in2"])
            def my_stream(msg: AssetDataMessage): ...

            def my_stream(msg: AssetDataMessage): ...
            app.stream(my_stream, assets=["asset1"], inputs=["in1"])

        The registered stream runs as an app task when the app connects.
        """

        if self.is_connected:
            raise RuntimeError("You cannot register streams after the KelvinApp is connected.")

        # Return a decorator when called without a function
        if fn is None:

            def decorator(inner: StreamFunc) -> AsyncFunc:
                return self.stream(inner, assets=assets, inputs=inputs)  # type: ignore[return-value]

            return decorator  # type: ignore[return-value]

        # Build the queue based on the provided filters
        # This uses the same helper used by windowing so semantics match there.
        def build_queue() -> Queue[AssetDataMessage]:
            a, i = self._default_assets_and_datastreams(assets, inputs)
            return self._apply_asset_datastream_filters(a, i)

        # Name the task for easier debugging
        stream_name = f"{fn.__module__}.{fn.__qualname__}"

        # Wrap the user's handler in a runner task that consumes from the queue forever
        async def runner() -> None:
            queue: Queue[AssetDataMessage] = build_queue()
            while True:
                msg = await queue.get()
                try:
                    if inspect.iscoroutinefunction(fn):
                        await fn(msg)
                    else:
                        # Run sync handlers off the main loop
                        await asyncio.to_thread(cast(StreamSyncFunc, fn), msg)
                except Exception as ex:
                    logger.error("Stream handler raised an exception", stream_name=stream_name, ex=ex)

        # Register the runner like any other task so it starts on connect
        self._tasks[stream_name] = runner  # type: ignore[assignment]

        # Return the runner (async) for completeness, matching task()/timer() behavior
        return runner  # type: ignore[return-value]

    # ----------------
    # Tasks
    # ----------------
    def task(
        self, fn: Optional[TaskFunc[P, R]] = None, *, name: Optional[str] = None
    ) -> Union[AsyncFunc[P, R], Callable[[TaskFunc[P, R]], AsyncFunc[P, R]]]:
        """
        Register a function as a task, either sync or async.

        This method acts as both a decorator and a decorator factory.
        It supports the following usage patterns:

            @app.task
            async def my_async_task(...): ...

            @app.task()
            def my_sync_task(...): ...

            @app.task(name="custom.task.name")
            def another_task(...): ...

            app.task(some_function)

        Parameters:
            fn (Optional[TaskFunc[P, R]]): The function to register. Can be sync or async.
                If not provided, a decorator is returned.
            name (Optional[str]): Optional name to register the task under.
                If not provided, the fully-qualified function name is used.

        Returns:
            If `fn` is provided, returns the async-compatible task wrapper.
            If `fn` is None, returns a decorator that can be applied to a function.
        """

        if self.is_connected:
            raise RuntimeError("You cannot register tasks after the KelvinApp is connected.")

        # no‐arg means “I want a decorator, not yet a function”
        if fn is None:

            def decorator(inner: TaskFunc[P, R]) -> AsyncFunc[P, R]:
                return self.task(inner, name=name)  # type: ignore[return-value]

            return decorator  # type: ignore[return-value]

        # here fn is the actual function to register
        task_name = name or f"{fn.__module__}.{fn.__qualname__}"

        if inspect.iscoroutinefunction(fn):
            self._tasks[task_name] = fn  # type: ignore[arg-type]
            return fn  # type: ignore[return-value]
        else:

            @functools.wraps(fn)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                return await asyncio.to_thread(cast(SyncFunc, fn), *args, **kwargs)  # type: ignore[return-value]

            self._tasks[task_name] = wrapper
            return wrapper  # type: ignore[return-value]

    def handle_task_result(self, task: asyncio.Task) -> None:
        task_name = task.get_name()
        try:
            # this will re‐raise the exception if one occurred
            task.result()
            logger.info("Task completed successfully", task_name=task_name)
        except asyncio.CancelledError:
            logger.info("Task was cancelled", task_name=task_name)
        except Exception as ex:
            logger.error("Task raised an exception", task_name=task_name, ex=ex)

        self._running_tasks.discard(task)  # Remove from running tasks

    async def _start_tasks(self) -> None:
        """
        Schedule all registered coroutine functions in self._tasks.
        Each task is named for easier debugging and removed from the set when done.
        """
        for task_name, coro_fn in self._tasks.items():
            logger.debug("Starting task", task_name=task_name)

            task = asyncio.create_task(coro_fn(), name=f"app-task:{task_name}")  # type: ignore
            task.add_done_callback(self.handle_task_result)

            # Add to running tasks
            self._running_tasks.add(task)

    async def _stop_tasks(self) -> None:
        """
        Cancel and await all running tasks, then clear the tracking set.
        Assumes a helper _cancel_task(task) exists to cancel and await the task.
        """
        for t in list(self._running_tasks):  # copy to avoid modifying during iteration
            await self._cancel_task(t)

    async def _cancel_task(self, task: Optional[asyncio.Task[Any]]) -> None:
        """
        Cancel a specific task and wait for it to finish.
        """
        if not task:
            return

        if task.done():
            return

        logger.debug("Cancelling task", task_name=task.get_name() or task)

        task.cancel()

    # ----------------
    # Tasks Timers
    # ----------------
    @overload
    def timer(self, fn: TaskFunc[[], Any], *, interval: float, name: Optional[str] = None) -> AsyncFunc[[], Any]: ...

    @overload
    def timer(
        self, *, interval: float, name: Optional[str] = None
    ) -> Callable[[TaskFunc[[], Any]], AsyncFunc[[], Any]]: ...

    def timer(
        self, fn: Optional[TaskFunc[[], Any]] = None, *, interval: float, name: Optional[str] = None
    ) -> Union[AsyncFunc[[], Any], Callable[[TaskFunc[[], Any]], AsyncFunc[[], Any]]]:
        """
        Register a function to be called at a repeating interval.

        Usage patterns:

            @app.timer(interval=5)
            def foo(): ...

            @app.timer(interval=5, name="my timer")
            async def foo(): ...

            def bar(): ...
            app.timer(bar, interval=10)
            app.timer(bar, interval=10, name="bar.timer")
        """

        if self.is_connected:
            raise RuntimeError("You cannot register timers after the KelvinApp is connected.")

        if fn is None:

            def decorator(inner: TaskFunc[[], Any]) -> AsyncFunc[[], Any]:
                return self.timer(inner, interval=interval, name=name)  # type: ignore[return-value]

            return decorator  # type: ignore[return-value]

        timer_name = name or f"{fn.__module__}.{fn.__qualname__}"

        async def wrapper() -> None:
            t = Timer(interval=interval, name=timer_name)
            async for _ in t:
                try:
                    if inspect.iscoroutinefunction(fn):
                        await fn()  # type: ignore[return-value]
                    else:
                        await asyncio.to_thread(fn)  # type: ignore[return-value]
                except Exception as ex:
                    logger.error("Timer raised an exception", timer_name=timer_name, ex=ex)

        self._tasks[timer_name] = wrapper
        return wrapper  # type: ignore[return-value]

    # ----------------
    # Run
    # ----------------
    async def run_forever(self) -> None:
        """
        Connects to the service and then waits indefinitely until cancelled.
        On cancellation, disconnects cleanly before propagating the cancellation.
        """
        # Get the current event loop
        loop = asyncio.get_running_loop()
        # Connect
        await self.connect()

        # Create an Event that is never set, so wait() blocks until cancelled.
        stop_event = asyncio.Event()

        # Register signal handlers
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, cast(Callable[[], None], lambda: stop_event.set()))

        try:
            await stop_event.wait()
        finally:
            # Ensure we disconnect cleanly
            await self.disconnect()

    def run(self) -> None:
        """
        Synchronous entry point:
        - Starts an asyncio event loop to run run_forever().
        - Blocks until run_forever() completes or is cancelled.
        - Allows Ctrl-C (KeyboardInterrupt) to stop cleanly.
        """
        # asyncio.run will set up the loop, run run_forever(), and close the loop.
        asyncio.run(self.run_forever())

    # ----------------
    # Public Helper Methods
    # ----------------
    def msg_is_control_change(self, msg: Message) -> TypeGuard[AssetDataMessage]:
        if not isinstance(msg.resource, KRNAssetDataStream) or not isinstance(msg.type, KMessageTypeData):
            return False

        try:
            resource = self.assets[msg.resource.asset].datastreams[msg.resource.data_stream]
        except KeyError:
            return False

        return resource.way in [WayEnum.input_cc_output, WayEnum.input_cc]
