import dataclasses
import statistics
import time
from collections import defaultdict
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from haystack.tracing import disable_tracing, enable_tracing
from haystack.tracing.tracer import Span, Tracer


@dataclasses.dataclass
class TimingSpan(Span):
    operation_name: str
    tags: dict = dataclasses.field(default_factory=dict)
    duration_ms: float = 0.0

    def set_tag(self, key: str, value: Any) -> None:
        self.tags[key] = value

    def set_content_tag(self, key: str, value: Any) -> None:
        pass

    def set_tags(self, tags: dict) -> None:
        self.tags.update(tags)

    def raw_span(self) -> Any:
        return self

    def get_correlation_data_for_logs(self) -> dict:
        return {}


class TimingTracer(Tracer):
    def __init__(self) -> None:
        self.spans: list[TimingSpan] = []

    def reset(self) -> None:
        self.spans = []

    @contextmanager
    def trace(
        self,
        operation_name: str,
        tags: dict | None = None,
        parent_span: Span | None = None,
    ) -> Iterator[TimingSpan]:
        start = time.perf_counter()
        span = TimingSpan(operation_name=operation_name, tags=dict(tags or {}))
        try:
            yield span
        finally:
            span.duration_ms = (time.perf_counter() - start) * 1000
            self.spans.append(span)

    def current_span(self) -> Span | None:
        return None

    def component_spans(self) -> list[TimingSpan]:
        return [s for s in self.spans if s.operation_name == "haystack.component.run"]

    def pipeline_span(self) -> TimingSpan | None:
        return next((s for s in self.spans if s.operation_name == "haystack.pipeline.run"), None)


@dataclasses.dataclass
class ComponentStats:
    name: str
    type: str
    p50_ms: float
    p95_ms: float
    p99_ms: float
    avg_ms: float
    pct_of_total: float


@dataclasses.dataclass
class BenchmarkResult:
    pipeline_file: str
    runs: int
    warmup: int
    errors: int
    components: list[ComponentStats]
    total_p50_ms: float
    total_p95_ms: float
    total_p99_ms: float
    total_avg_ms: float
    total_min_ms: float
    total_max_ms: float

    def to_dict(self) -> dict:
        return {
            "pipeline_file": self.pipeline_file,
            "runs": self.runs,
            "warmup": self.warmup,
            "errors": self.errors,
            "components": [dataclasses.asdict(c) for c in self.components],
            "total": {
                "p50_ms": self.total_p50_ms,
                "p95_ms": self.total_p95_ms,
                "p99_ms": self.total_p99_ms,
                "avg_ms": self.total_avg_ms,
                "min_ms": self.total_min_ms,
                "max_ms": self.total_max_ms,
            },
        }


class PipelineBenchmark:
    """
    Benchmark a Haystack Pipeline and return performance statistics for overall
    pipeline execution as well as individual component
    """

    def run(
        self,
        pipeline: Any,
        inputs: dict,
        pipeline_file: str,
        runs: int = 10,
        warmup: int = 1,
    ) -> BenchmarkResult:
        component_durations: dict[str, list[float]] = defaultdict(list)
        component_types: dict[str, str] = {}
        pipeline_durations: list[float] = []
        errors = 0

        timing_tracer = TimingTracer()
        enable_tracing(timing_tracer)

        try:
            for i in range(warmup + runs):
                timing_tracer.reset()
                try:
                    pipeline.run(inputs)
                except Exception:
                    errors += 1
                    continue

                if i < warmup:
                    continue

                for span in timing_tracer.component_spans():
                    name = span.tags.get("haystack.component.name", "unknown")
                    ctype = span.tags.get("haystack.component.type", "unknown")
                    component_durations[name].append(span.duration_ms)
                    component_types[name] = ctype

                ps = timing_tracer.pipeline_span()
                if ps:
                    pipeline_durations.append(ps.duration_ms)
        finally:
            disable_tracing()

        total_avg = statistics.mean(pipeline_durations) if pipeline_durations else 1.0
        total_s = _stats(pipeline_durations)

        components = [
            ComponentStats(
                name=name,
                type=component_types[name],
                pct_of_total=round((statistics.mean(durations) / total_avg) * 100, 1),
                **{f"{k}_ms": v for k, v in _stats(durations).items() if k not in ("min", "max")},
            )
            for name, durations in component_durations.items()
        ]

        return BenchmarkResult(
            pipeline_file=pipeline_file,
            runs=runs,
            warmup=warmup,
            errors=errors,
            components=components,
            total_p50_ms=total_s["p50"],
            total_p95_ms=total_s["p95"],
            total_p99_ms=total_s["p99"],
            total_avg_ms=total_s["avg"],
            total_min_ms=total_s["min"],
            total_max_ms=total_s["max"],
        )


def _stats(durations: list[float]) -> dict:
    if not durations:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "avg": 0.0, "min": 0.0, "max": 0.0}

    if len(durations) >= 4:
        q = statistics.quantiles(durations, n=100)
        p50, p95, p99 = q[49], q[94], q[98]
    else:
        p50 = statistics.median(durations)
        p95 = p99 = max(durations)

    return {
        "p50": round(p50, 2),
        "p95": round(p95, 2),
        "p99": round(p99, 2),
        "avg": round(statistics.mean(durations), 2),
        "min": round(min(durations), 2),
        "max": round(max(durations), 2),
    }
