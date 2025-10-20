import collections
from collections.abc import Callable, Iterable, Sequence

import attrs
from loguru import logger

from liblaf.grapes import pretty
from liblaf.grapes.logging import helper
from liblaf.grapes.sentinel import NOP

from ._clock import ClockName, clock
from ._statistics import StatisticName, pretty_statistic
from .defaults import (
    DEFAULT_CLOCKS,
    LOG_RECORD_DEFAULT_INDEX,
    LOG_RECORD_DEFAULT_LEVEL,
    LOG_RECORD_DEFAULT_THRESHOLD_SEC,
    LOG_SUMMARY_DEFAULT_LEVEL,
    LOG_SUMMARY_DEFAULT_STATISTICS,
)


@attrs.define
class Timings:
    name: str | None = attrs.field(default=None)
    clocks: Sequence[ClockName] = attrs.field(default=DEFAULT_CLOCKS)
    timings: dict[ClockName, list[float]] = attrs.field(
        factory=lambda: collections.defaultdict(list), init=False
    )

    _start_time: dict[ClockName, float] = attrs.field(factory=dict, init=False)
    _stop_time: dict[ClockName, float] = attrs.field(factory=dict, init=False)

    def __len__(self) -> int:
        return len(self.timings[self.default_clock])

    @property
    def default_clock(self) -> ClockName:
        return self.clocks[0]

    def clear(self) -> None:
        self.timings.clear()
        self._start_time.clear()
        self._stop_time.clear()

    def elapsed(self, clock_name: ClockName | None = None) -> float:
        clock_name = clock_name or self.default_clock
        stop_time: float
        if clock_name in self._stop_time:
            stop_time = self._stop_time[clock_name]
        else:
            stop_time = clock(clock_name)
        return stop_time - self._start_time[clock_name]

    @helper
    def log_record(
        self,
        *,
        index: int = LOG_RECORD_DEFAULT_INDEX,
        level: int | str = LOG_RECORD_DEFAULT_LEVEL,
        threshold_sec: float | None = LOG_RECORD_DEFAULT_THRESHOLD_SEC,
    ) -> None:
        if threshold_sec is not None and self.elapsed() < threshold_sec:
            return
        logger.opt(depth=helper.depth).log(level, self.pretty_record(index=index))

    @helper
    def log_summary(
        self,
        *,
        level: int | str = LOG_SUMMARY_DEFAULT_LEVEL,
        stats: Iterable[StatisticName] = LOG_SUMMARY_DEFAULT_STATISTICS,
    ) -> None:
        logger.opt(depth=helper.depth).log(level, self.pretty_summary(stats=stats))

    def pretty_record(self, index: int = LOG_RECORD_DEFAULT_INDEX) -> str:
        name: str = self.name or "Timer"
        items: list[str] = [
            f"{clock_name}: {pretty.pretty_duration(self.timings[clock_name][index])}"
            for clock_name in self.clocks
        ]
        items_str: str = ", ".join(items)
        return f"{name} > {items_str}"

    def pretty_summary(
        self, stats: Iterable[StatisticName] = LOG_SUMMARY_DEFAULT_STATISTICS
    ) -> str:
        name: str = self.name or "Timer"
        header: str = f"{name} (count: {len(self)})"
        if len(self) == 0:
            return header
        lines: list[str] = []
        for clock_name in self.clocks:
            stats_str: list[str] = []
            for stat in stats:
                stat_name: str
                value: str
                stat_name, value = pretty_statistic(self.timings[clock_name], stat)
                stats_str.append(f"{stat_name}: {value}")
            line: str = f"{clock_name} > {', '.join(stats_str)}"
            lines.append(line)
        if len(self.clocks) == 1:
            return f"{header} {lines[0]}"
        return f"{header}\n" + "\n".join(lines)


type Callback = Callable[[Timings], None] | NOP
