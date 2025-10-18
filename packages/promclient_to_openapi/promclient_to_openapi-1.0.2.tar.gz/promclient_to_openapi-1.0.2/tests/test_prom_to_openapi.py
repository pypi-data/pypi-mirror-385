"""Tests for promclient_to_openapi."""

import hashlib
import json

from prometheus_client import REGISTRY, Gauge

from promclient_to_openapi import prometheus_client_to_openapi
from promclient_to_openapi.utils import normalize_describe_labels, snake_to_pascal

m1 = Gauge(name="test_metric_foo", documentation="Test metric", labelnames=("metric",))
m1.labels(("1",)).set(value=1)

m2 = Gauge(name="test_metric_bar", documentation="Test metric", labelnames=("metric",))
m2.labels(("2",)).set(value=2)


def test_pascalize() -> None:
    """Test converting snake_case to PascalCase."""

    assert snake_to_pascal("test_string_foo_bar") == "TestStringFooBar"


def test_normalize_describe_labels() -> None:
    """Test describe_labels argument normalization."""

    test_arg = {"TeSt": {"FoO": "bAr"}}
    test_res = {"test": {"foo": "bAr"}}

    assert normalize_describe_labels(None) == {}
    assert normalize_describe_labels(test_arg) == test_res


def test_sync_from_text_defaults() -> None:
    """Test default collectors schema generated from metrics text."""

    t = json.dumps(prometheus_client_to_openapi(metrics=REGISTRY)).encode(encoding="utf-8")
    md5 = hashlib.md5(t).hexdigest()  # noqa: S324
    assert md5 == "7625a4123f3685a2c5128f6a97c76863"


def test_sync_from_text_custom() -> None:
    """Test default collectors schema generated from metrics text with labels."""

    labels_descriptions: dict[str, dict[str, str]] = {
        "python_info": {
            "major": "Python major  version number",
            "minor": "Python minor version number",
            "patchlevel": "Python patchlevel version number",
            "implementation": "Python implementation",
            "version": "Python version string",
        },
    }

    t = json.dumps(
        prometheus_client_to_openapi(
            metrics=REGISTRY,
            describe_labels=labels_descriptions,
            description="Customized description",
            property_name="MyCoolMetrics",
        ),
    ).encode(encoding="utf-8")
    md5 = hashlib.md5(t).hexdigest()  # noqa: S324
    assert md5 == "6c5ba5ecee6e4b101c5ef9d880d0fea5"


def test_sync_from_metrics_defaults() -> None:
    """Test schema generation with dummy metrics."""

    t = json.dumps(prometheus_client_to_openapi(metrics=(m1, m2))).encode(encoding="utf-8")
    md5 = hashlib.md5(t).hexdigest()  # noqa: S324
    assert md5 == "a090a909534fd733cdda2dabc428808d"


def test_sync_from_metrics_custom() -> None:
    """Test schema generation with dummy metrics."""

    labels_descriptions: dict[str, dict[str, str]] = {"metric": {"label": "Test label"}}
    t = json.dumps(
        prometheus_client_to_openapi(
            metrics=(m1, m2),
            describe_labels=labels_descriptions,
            description="Customized description",
            property_name="MyCoolMetrics",
        ),
    ).encode(encoding="utf-8")
    md5 = hashlib.md5(t).hexdigest()  # noqa: S324
    assert md5 == "b024abb21c51a0f5bdce147b64aa735e"
