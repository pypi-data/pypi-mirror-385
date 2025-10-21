import asyncio
import time
from typing import AsyncIterator

import structlog

MAX_DRIFT_PERCENT = 0.30
MAX_DRIFT_CEILING = 1.2

logger = structlog.get_logger()


class Timer:
    """A repeating async timer that corrects clock drift."""

    def __init__(self, interval: float, name: str, max_drift_correction: float = 0.1):
        self.interval = interval
        self.name = name

        # Log drift if it exceeds this threshold
        self.max_drift = min(self.interval * MAX_DRIFT_PERCENT, MAX_DRIFT_CEILING)

        # When drift correction is enabled, enforce minimum/maximum intervals
        if self.interval > max_drift_correction:
            self.min_interval = self.interval - max_drift_correction
            self.max_interval = self.interval + max_drift_correction
        else:
            self.min_interval = self.max_interval = self.interval

        # Initial time references
        self.epoch = time.perf_counter()
        self.last_wakeup_at = self.epoch
        self.last_yield_at = self.epoch

        self.iteration = 0
        self.overlaps = 0

    async def __aiter__(self) -> AsyncIterator[float]:
        """An async iterator that yields the actual sleep interval each loop."""
        while True:
            sleep_time = self._tick()
            await asyncio.sleep(sleep_time)
            self.last_yield_at = time.perf_counter()
            yield sleep_time

    def _tick(self) -> float:
        """Calculate how long to sleep next time, correcting for drift."""
        now = time.perf_counter()

        # First iteration: just return the given interval
        if self.last_yield_at == self.epoch:
            self.iteration += 1
            self.last_wakeup_at = now
            return self.interval

        time_spent_sleeping = self.last_yield_at - self.last_wakeup_at
        time_spent_yielding = now - self.last_wakeup_at - time_spent_sleeping

        drift = self.interval - time_spent_sleeping
        new_interval = self.interval + drift
        if drift > 0:
            new_interval = min(new_interval, self.max_interval)
        else:
            new_interval = max(new_interval, self.min_interval)

        logger.debug(
            "Timer fired",
            name=self.name,
            iteration=self.iteration,
            sleeptime=round(time_spent_sleeping, 6),
            runtime=round(time_spent_yielding, 6),
            drift=round(abs(drift), 6),
            new_interval=round(new_interval, 6),
            since_epoch=round(now - self.epoch, 6),
        )

        # Warn if the total time running exceeds the interval
        if time_spent_yielding > self.interval:
            self.overlaps += 1
            logger.warning(
                "Timer is overlapping",
                name=self.name,
                interval=round(self.interval, 6),
                runtime=round(time_spent_yielding, 6),
            )

        self.iteration += 1
        self.last_wakeup_at = now
        self.interval = new_interval

        return new_interval
