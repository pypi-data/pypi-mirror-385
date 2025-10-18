"""Translates prometheus_client metrics to OpenAPI."""

from collections.abc import Iterable
from typing import Any

from prometheus_client.metrics import MetricWrapperBase
from prometheus_client.metrics_core import Metric
from prometheus_client.registry import Collector, CollectorRegistry

from promclient_to_openapi.utils import normalize_describe_labels, snake_to_pascal


def prometheus_client_to_openapi(
    metrics: CollectorRegistry | Iterable[MetricWrapperBase],
    describe_labels: dict[str, dict[str, str]] | None = None,
    property_name: str = "PrometheusClientMetrics",
    description: str = "Prometheus-compatible metrics",
) -> dict[str, Any]:
    """
    Produce OpenAPI schema from prometheus_client library.

    If metrics argument is registry, this will collect the actual metrics and
    parse text back. Suitable when various collectors are used.

    If metrics argument is list of metrics (like `Gauge`, `Counter`, `Info`,
    etc), no metric generation will be invoked.

    Args:
        metrics: Collector registry to generate metrics or list of actual metrics objects.
        describe_labels: Mapping metric names to dictionaries with label names and descriptions.
        property_name: Main property name.
        description: Main property description.

    Returns:
        Dictionary of schema to be converted to OpenAPI JSON.
    """

    # Normalized dict[str, dict[str, str]].
    labels_descriptions = normalize_describe_labels(describe_labels)

    schemas: dict[str, Any] = {
        property_name: {
            "properties": {},
            "type": "object",
            "title": property_name,
            "description": description,
        },
    }

    # prometheus_client library have two types of entities: for example, a Gauge
    # and a GaugeMetricFamily. As a programmer, you may initialize a Gauge once
    # on top of your module, which will generate second type as standalone
    # collector and add it to Registry object.
    #
    # Or you can write your own Collector class with .collect() generator which
    # should yield *MetricFamily instances.
    #
    # In this case we can use generate_latest() to render text metrics (call
    # every collector's .collect() method under the hood) or iterate by owselves)

    # Case 1 -- provided a full CollectorRegistry() (e.g. default REGISTRY) with
    # possibly unpopulated metrics (without samples).
    families: Iterable[Metric] | Iterable[MetricWrapperBase] = []
    if isinstance(metrics, CollectorRegistry):
        # This is kinda easier:
        #
        # text = generate_latest(registry=metrics).decode(encoding="utf-8")  # noqa: ERA001
        # families = text_string_to_metric_families(text=text)  # noqa: ERA001

        # Get all the actuall collectors (either custom ones such as
        # ProcessCollector or just a "metrics" such as Gauge() which is an
        # instance of Collector() actually) exploiting internal dictionary of
        # collectors.
        collector: Collector
        for collector in metrics._names_to_collectors.values():  # pyright: ignore[reportPrivateUsage]  # noqa: SLF001

            # To be safe because .collect() may be a generator and a function
            # with returned iterable.
            for metric in collector.collect():
                families.append(metric)

    # Case 2 -- provided iterable of MetricWrappers (such as Gauge() or
    # Counter()). Just copy those wrappers for next loop to handle
    else:
        families = metrics

    for metric in families:
        if isinstance(metric, Metric):
            metric_name_pascalized = snake_to_pascal(metric.name)
            metric_name = metric.name
            metric_description = metric.documentation

        elif isinstance(metric, MetricWrapperBase):  # pyright: ignore[reportUnnecessaryIsInstance]
            metric_name_pascalized = snake_to_pascal(metric._name)  # pyright: ignore[reportPrivateUsage, reportUnknownArgumentType, reportUnknownMemberType]  # noqa: SLF001
            metric_name: str = metric._name  # pyright: ignore[reportUnknownVariableType, reportPrivateUsage, reportUnknownMemberType]  # noqa: SLF001
            metric_description = metric._documentation  # pyright: ignore[reportPrivateUsage] # noqa: SLF001

        else:
            msg = f"Unknown metric type: {type(metric)}"
            raise NotImplementedError(msg)

        schemas[property_name]["properties"][metric_name] = {
            "$ref": f"#/components/schemas/{metric_name_pascalized}",
        }

        schemas[metric_name_pascalized] = {
            "properties": {},
            "type": "object",
            "title": metric_name_pascalized,
            "description": metric_description,
        }

        # No idea why PyRight assumes those are not strings.
        this_metric_labels_descriptions: dict[str, str] = labels_descriptions.get(metric_name.lower(), {})  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
        for label_name, label_description in this_metric_labels_descriptions.items():
            schemas[metric_name_pascalized]["properties"][label_name] = {
                "type": "string",
                "description": label_description,
                "title": label_name.capitalize(),
            }

    return schemas
