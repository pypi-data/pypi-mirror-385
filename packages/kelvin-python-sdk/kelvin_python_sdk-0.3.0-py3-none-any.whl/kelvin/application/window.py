from __future__ import annotations

import asyncio
import math
import time
from collections import deque
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator, Dict, List, Literal, Optional, Tuple

import structlog

from kelvin.application.timer import Timer
from kelvin.message import AssetDataMessage

try:
    import pandas as pd
except ImportError as e:
    raise ImportError(
        "Missing requirements to use this feature. Install with `pip install 'kelvin-python-sdk[ai]'`"
    ) from e

UTC = timezone.utc
logger = structlog.get_logger()


# -----------------------------
# Time utilities
# -----------------------------


def _ensure_tz(dt: datetime) -> datetime:
    """Return a timezone-aware datetime.

    If the input is naive, assume UTC. This avoids raising and supports callers
    that do not attach tzinfo. No wall-clock conversion is attempted.
    """
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        return dt.replace(tzinfo=UTC)
    return dt


def quantize_time(
    dt: datetime,
    step: Optional[timedelta] = None,
    *,
    mode: Literal["nearest", "floor", "ceil"] = "nearest",
    anchor: Optional[datetime] = None,
) -> datetime:
    """Quantize a datetime to a fixed step.

    - Accepts naive datetimes and treats them as UTC.
    - Uses integer microseconds to avoid floating-point rounding issues.
    - If step is None, return the input unchanged.

    Parameters
    ----------
    dt : datetime
        Timestamp to quantize. Naive values are interpreted as UTC.
    step : timedelta or None
        Quantization step. When None, no quantization is applied.
    mode : {"nearest", "floor", "ceil"}
        Rounding mode. Defaults to "nearest".
    anchor : datetime or None
        Grid anchor. When None, use the Unix epoch at UTC.

    Returns
    -------
    datetime
        Quantized datetime with the same tzinfo semantics as input, normalized to UTC if naive.
    """
    if step is None:
        return _ensure_tz(dt)

    dt = _ensure_tz(dt)

    if anchor is None:
        anchor = datetime(1970, 1, 1, tzinfo=UTC)
    else:
        anchor = _ensure_tz(anchor)

    # integer microseconds prevent float drift
    delta = dt - anchor
    step_us = int(step.total_seconds() * 1_000_000)
    if step_us <= 0:
        raise ValueError("step must be a positive timedelta")

    delta_us = int(delta.total_seconds() * 1_000_000)

    if mode == "nearest":
        q = int((delta_us + step_us / 2) // step_us)
    elif mode == "floor":
        q = delta_us // step_us
    else:  # "ceil"
        q = math.ceil(delta_us / step_us)

    snapped = anchor + timedelta(microseconds=q * step_us)
    return snapped.astimezone(dt.tzinfo)


def round_nearest_time(dt: datetime, round_to: Optional[timedelta] = None) -> datetime:
    """Backwards-compatible wrapper that rounds to the nearest tick."""
    return quantize_time(dt, round_to, mode="nearest")


# -----------------------------
# Base window with buffering
# -----------------------------


class BaseWindow:
    """Manage per-asset in-memory buffers and DataFrames for streaming data.

    Design
    ------
    - Each asset has a deque of (timestamp, {stream: payload}). The deque can be bounded by `buffer_size`.
    - Timestamps are normalized to UTC and optionally quantized.
    - DataFrames are per asset, indexed by UTC timestamps, with columns equal to `inputs`.
    - Duplicate timestamps within a buffer are merged into a single row before appending.
    """

    def __init__(
        self,
        assets: List[str],
        inputs: List[str],
        queue: "asyncio.Queue[AssetDataMessage]",
        *,
        round_to: Optional[timedelta] = None,
        buffer_size: Optional[int] = None,
    ) -> None:
        # validate inputs
        if not isinstance(assets, list) or not assets or not all(isinstance(a, str) and a.strip() for a in assets):
            raise ValueError("assets must be a list of non-empty strings")
        if not isinstance(inputs, list) or not inputs or not all(isinstance(i, str) and i.strip() for i in inputs):
            raise ValueError("inputs must be a list of non-empty strings")
        if not isinstance(queue, asyncio.Queue):
            raise ValueError("queue must be an asyncio.Queue instance")
        if round_to is not None and (not isinstance(round_to, timedelta) or round_to <= timedelta()):
            raise ValueError("round_to must be a positive timedelta or None")
        if buffer_size is not None and (not isinstance(buffer_size, int) or buffer_size <= 0):
            raise ValueError("buffer_size must be a positive integer or None")

        self.queue = queue
        self.assets = assets
        self.inputs = inputs
        self.round_to = round_to

        # in-memory buffers: asset -> deque of (timestamp, {stream: payload})
        self._buffers: Dict[str, deque] = {asset: deque(maxlen=buffer_size) for asset in assets}
        self.dataframes: Dict[str, pd.DataFrame] = {}

        # watermark used by time windows. None until the first emission.
        self.current_watermark: Optional[datetime] = None

    def _append_buffer(
        self,
        msg: AssetDataMessage,
        *,
        window_start: Optional[datetime] = None,
        allowed_lateness: Optional[timedelta] = None,
    ) -> None:
        """Append a message to the per-asset buffer with basic filtering.

        - Normalizes and quantizes the message timestamp.
        - Drops messages for unknown assets or streams.
        - If `window_start` is supplied, drops events that are older than the allowed lateness.
        """
        ts = quantize_time(msg.timestamp, self.round_to).astimezone(UTC)

        asset = msg.resource.asset
        data_stream = msg.resource.data_stream

        if asset not in self.assets:
            logger.warning("Dropping message for unknown asset", asset=asset, stream=data_stream)
            return
        if data_stream not in self.inputs:
            logger.warning("Dropping message for unknown stream", asset=asset, stream=data_stream)
            return

        if window_start is not None:
            ws = _ensure_tz(window_start).astimezone(UTC)
            if allowed_lateness is None:
                if ts < ws:
                    logger.warning("Dropping message before window start", asset=asset, stream=data_stream)
                    return
            else:
                if ts < ws - allowed_lateness:
                    logger.warning("Dropping message older than allowed lateness", asset=asset, stream=data_stream)
                    return

        self._buffers[asset].append((ts, {data_stream: msg.payload}))

    def _build_frame_from_buffer(self, items: List[Tuple[datetime, Dict[str, object]]]) -> pd.DataFrame:
        """Merge duplicate timestamps and construct a DataFrame for a batch of items."""
        merged: Dict[datetime, Dict[str, object]] = {}
        for ts, row in items:
            if ts not in merged:
                merged[ts] = dict(row)
            else:
                merged[ts].update(row)

        timestamps = sorted(merged.keys())
        rows = [merged[ts] for ts in timestamps]
        df = pd.DataFrame(rows, index=pd.DatetimeIndex(timestamps, tz=UTC))
        df = df.reindex(columns=self.inputs)
        return df

    def _set_asset_df(self, asset: str, buffer: deque, slice_from: Optional[int] = None) -> pd.DataFrame:
        """Append buffered rows to the asset DataFrame with minimal sorting.

        Sorting is skipped when the incoming batch is monotonically newer than the
        existing index. Otherwise a single sort_index is performed after concat.
        """
        window_items = list(buffer)[slice_from:]
        buffer_df = self._build_frame_from_buffer(window_items)

        if asset not in self.dataframes:
            self.dataframes[asset] = buffer_df
        else:
            existing = self.dataframes[asset]
            if not existing.empty and not buffer_df.empty:
                newest_incoming = buffer_df.index[-1]
                if existing.index.is_monotonic_increasing and newest_incoming >= existing.index[-1]:
                    self.dataframes[asset] = pd.concat([existing, buffer_df], axis=0, sort=False)
                else:
                    self.dataframes[asset] = pd.concat([existing, buffer_df], axis=0, sort=False).sort_index()
            else:
                self.dataframes[asset] = pd.concat([existing, buffer_df], axis=0, sort=False)

        return self.dataframes[asset]

    def _flush_buffers(self) -> None:
        """Flush all per-asset buffers into DataFrames in a single pass."""
        start = time.perf_counter()
        total_assets = 0
        total_points = 0

        for asset, buffer in self._buffers.items():
            if not buffer:
                continue
            total_assets += 1
            total_points += len(buffer)
            self._set_asset_df(asset, buffer)
            buffer.clear()

        duration = round(time.perf_counter() - start, 4)
        logger.debug("Window: flushed buffers", duration=duration, total_assets=total_assets, total_points=total_points)

    def get_df(self, asset_name: str) -> pd.DataFrame:
        """Return a copy of the DataFrame for the asset or an empty shell.

        The returned DataFrame has a UTC DatetimeIndex and columns equal to `inputs`.
        When the asset has not produced data yet, return an empty DataFrame with the
        correct index and columns.
        """
        df = self.dataframes.get(asset_name)
        if df is not None:
            return df.copy()
        return pd.DataFrame(index=pd.DatetimeIndex([], name="timestamp", tz=UTC), columns=self.inputs)


# -----------------------------
# Time-based windows
# -----------------------------


class BaseTimeWindow(BaseWindow):
    """Time-based windowing of data streams.

    Parameters
    ----------
    assets : list[str]
        Asset identifiers to include.
    inputs : list[str]
        Data stream identifiers to include as DataFrame columns.
    queue : asyncio.Queue[AssetDataMessage]
        Source of incoming messages.
    window_size : timedelta
        Duration of each window.
    hop_size : timedelta
        Time between the start of consecutive windows.
    round_to : timedelta or None
        Optional timestamp quantization step.
    align_step : timedelta or None
        Optional alignment step for initial window start. If None, no extra alignment.
    allowed_lateness : timedelta or None
        If provided, accept events older than `window_start` by up to this amount.
    buffer_size : int or None
        Optional bound for per-asset buffer deques.

    Notes
    -----
    - Naive `window_start` values are interpreted as UTC.
    - Message timestamps that are naive are also treated as UTC.
    """

    def __init__(
        self,
        assets: List[str],
        inputs: List[str],
        queue: "asyncio.Queue[AssetDataMessage]",
        window_size: timedelta,
        hop_size: timedelta,
        *,
        round_to: Optional[timedelta] = None,
        align_step: Optional[timedelta] = None,
        allowed_lateness: Optional[timedelta] = None,
        buffer_size: Optional[int] = None,
    ) -> None:
        super().__init__(
            assets=assets,
            inputs=inputs,
            queue=queue,
            round_to=round_to,
            buffer_size=buffer_size,
        )

        if window_size <= timedelta():
            raise ValueError("window_size must be a positive timedelta")
        if hop_size <= timedelta():
            raise ValueError("hop_size must be a positive timedelta")

        self.window_size = window_size
        self.hop_size = hop_size
        self.align_step = align_step
        self.allowed_lateness = allowed_lateness

    async def _drain(self, ws: datetime) -> None:
        """Drain the queue non-blocking and append to buffers."""
        start = time.perf_counter()
        total_msgs = 0

        while True:
            try:
                msg = self.queue.get_nowait()
                total_msgs += 1
            except asyncio.QueueEmpty:
                break
            else:
                self._append_buffer(msg, window_start=ws, allowed_lateness=self.allowed_lateness)

        duration = round(time.perf_counter() - start, 4)
        logger.debug("Window: drained queue", window_start=ws, duration=duration, total_msgs=total_msgs)

    def _slice_and_prune(self, ws: datetime) -> List[Tuple[str, pd.DataFrame]]:
        """Slice frames for the active window and prune older rows."""
        start = time.perf_counter()

        we = ws + self.window_size
        self._flush_buffers()

        outputs: List[Tuple[str, pd.DataFrame]] = []
        for asset, df in self.dataframes.items():
            if df.empty:
                outputs.append((asset, df))
                continue
            mask = (df.index >= ws) & (df.index < we)
            slice_df = df.loc[mask]
            outputs.append((asset, slice_df))
            # prune rows older than ws
            self.dataframes[asset] = df.loc[df.index >= ws]

        self.current_watermark = ws

        duration = round(time.perf_counter() - start, 4)
        logger.debug("Window: emitting", window_start=ws, window_end=we, duration=duration, total_windows=len(outputs))

        return outputs

    async def stream(self, window_start: Optional[datetime] = None) -> AsyncGenerator[Tuple[str, pd.DataFrame], None]:
        """Continuously emit windowed DataFrames per asset.

        Behavior
        --------
        - Align the first emission to `window_start + window_size`.
        - Sleep until that first boundary, then drain and emit.
        - Continue emitting every `hop_size` using a `Timer`.

        Parameters
        ----------
        window_start : datetime or None
            Start of the first window. When None, use current UTC time. Naive values are
            interpreted as UTC. The start is optionally aligned by `align_step`.
        """
        if window_start is None:
            window_start = datetime.now(UTC)
        else:
            window_start = _ensure_tz(window_start)

        window_start = quantize_time(window_start.astimezone(UTC), self.align_step, mode="floor")

        # align to the first window end
        first_end = window_start + self.window_size
        now = datetime.now(UTC)
        sleep = max((first_end - now).total_seconds(), 0)
        if sleep:
            await asyncio.sleep(sleep)

        # first emission
        await self._drain(window_start)
        for asset, df in self._slice_and_prune(window_start):
            yield asset, df

        # subsequent hops
        window_start += self.hop_size
        timer = Timer(self.hop_size.total_seconds(), name="BaseTimeWindow")
        async for _ in timer:
            await self._drain(window_start)
            for asset, df in self._slice_and_prune(window_start):
                yield asset, df
            window_start += self.hop_size


class TumblingWindow(BaseTimeWindow):
    """Non-overlapping time windows where hop_size equals window_size."""

    def __init__(
        self,
        assets: List[str],
        inputs: List[str],
        queue: "asyncio.Queue[AssetDataMessage]",
        window_size: timedelta,
        *,
        round_to: Optional[timedelta] = None,
        align_step: Optional[timedelta] = None,
        allowed_lateness: Optional[timedelta] = None,
        buffer_size: Optional[int] = None,
    ) -> None:
        super().__init__(
            assets=assets,
            inputs=inputs,
            queue=queue,
            window_size=window_size,
            hop_size=window_size,
            round_to=round_to,
            align_step=align_step,
            allowed_lateness=allowed_lateness,
            buffer_size=buffer_size,
        )


class HoppingWindow(BaseTimeWindow):
    """Overlapping time windows when hop_size is smaller than window_size."""

    def __init__(
        self,
        assets: List[str],
        inputs: List[str],
        queue: "asyncio.Queue[AssetDataMessage]",
        window_size: timedelta,
        hop_size: timedelta,
        *,
        round_to: Optional[timedelta] = None,
        align_step: Optional[timedelta] = None,
        allowed_lateness: Optional[timedelta] = None,
        buffer_size: Optional[int] = None,
    ) -> None:
        super().__init__(
            assets=assets,
            inputs=inputs,
            queue=queue,
            window_size=window_size,
            hop_size=hop_size,
            round_to=round_to,
            align_step=align_step,
            allowed_lateness=allowed_lateness,
            buffer_size=buffer_size,
        )


# -----------------------------
# Rolling windows
# -----------------------------


class RollingWindow(BaseWindow):
    """Rolling window based on a fixed count of messages per asset.

    Notes
    -----
    - The internal per-asset deque is bounded to prevent unbounded growth.
    - The DataFrame yielded for an asset represents the last `count_size` items after merging
      duplicate timestamps inside that slice.
    """

    def __init__(
        self,
        assets: List[str],
        inputs: List[str],
        queue: "asyncio.Queue[AssetDataMessage]",
        count_size: int,
        *,
        slide: int = 1,
        round_to: Optional[timedelta] = None,
        buffer_size: Optional[int] = None,
    ) -> None:
        if count_size <= 0:
            raise ValueError("count_size must be positive")
        if slide <= 0:
            raise ValueError("slide must be positive")

        # provide a safe default bound when not supplied
        if buffer_size is None:
            buffer_size = max(count_size * 4, 1024)

        super().__init__(
            assets=assets,
            inputs=inputs,
            queue=queue,
            round_to=round_to,
            buffer_size=buffer_size,
        )

        self.count_size = int(count_size)
        self.slide = int(slide)

    async def stream(self) -> AsyncGenerator[Tuple[str, pd.DataFrame], None]:
        """Continuously emit rolling windows as new messages arrive."""
        while True:
            msg = await self.queue.get()
            asset = msg.resource.asset
            self._append_buffer(msg)

            buf = self._buffers[asset]
            if len(buf) < self.count_size:
                continue

            window_items = list(buf)[-self.count_size :]  # noqa: E203
            df_window = self._build_frame_from_buffer(window_items).sort_index()
            self.dataframes[asset] = df_window
            yield asset, df_window.copy()

            # slide the buffer by dropping the oldest `slide` items
            drops = min(self.slide, len(buf))
            for _ in range(drops):
                buf.popleft()
