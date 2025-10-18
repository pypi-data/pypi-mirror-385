Generate OpenAPI components schema from [`prometheus_client`](https://pypi.org/project/prometheus-client/) metrics.

## Install

```bash
pip install promclient_to_openapi
```

## Usage

```python
import json

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from promclient_to_openapi import prometheus_client_to_openapi
from prometheus_client import REGISTRY


app = FastAPI()
metrics_schema = prometheus_client_to_openapi(metrics=REGISTRY)


def custom_openapi():
    """Modify default OpenAPI spec for metrics to be documented."""

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(title="Customized OpenAPI", version="0.1.0", routes=app.routes)
    openapi_schema["components"] = {"schemas": metrics_schema}

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

See more about OpenAPI customization for FastAPI on the [docs](https://fastapi.tiangolo.com/how-to/extending-openapi/).

Or you can provide your list of metrics objects (`Gauge`, `Counter`, `Info`, etc) instead of invoking full metrics generation and parsing and also customize description, root property name and describe labels:

```python

m1 = Gauge(name="test_metric_foo", documentation="Test metric", labelnames=("metric",))
m1.labels(("1",)).set(value=1)

m2 = Gauge(name="test_metric_bar", documentation="Test metric", labelnames=("metric",))
m2.labels(("2",)).set(value=2)

labels_descriptions: dict[str, str] = {"Test metric": {"metric": "Test label"}}

metrics_schema = prometheus_client_to_openapi(
    metrics=(m1, m2),
    describe_labels=labels_descriptions,
    description="Customized description",
    roperty_name="MyCoolMetrics"
)
```

**For more advanced usage see below**.

First example will generate default valid OpenAPI schema extended with default `prometheus_client` metrics definitions:

```yaml
openapi: 3.1.0
info:
  title: Customized OpenAPI
  version: 0.1.0
paths: {}
components:
  schemas:
    PrometheusClientMetrics:
      properties:
        python_gc_objects_collected:
          $ref: '#/components/schemas/PythonGcObjectsCollected'
        python_gc_objects_uncollectable:
          $ref: '#/components/schemas/PythonGcObjectsUncollectable'
        python_gc_collections:
          $ref: '#/components/schemas/PythonGcCollections'
        python_info:
          $ref: '#/components/schemas/PythonInfo'
        process_virtual_memory_bytes:
          $ref: '#/components/schemas/ProcessVirtualMemoryBytes'
        process_resident_memory_bytes:
          $ref: '#/components/schemas/ProcessResidentMemoryBytes'
        process_start_time_seconds:
          $ref: '#/components/schemas/ProcessStartTimeSeconds'
        process_cpu_seconds:
          $ref: '#/components/schemas/ProcessCpuSeconds'
        process_open_fds:
          $ref: '#/components/schemas/ProcessOpenFds'
        process_max_fds:
          $ref: '#/components/schemas/ProcessMaxFds'
      type: object
      title: PrometheusClientMetrics
      description: Prometheus-compatible metrics
    PythonGcObjectsCollected:
      properties:
        generation:
          type: string
          title: Generation
      type: object
      title: PythonGcObjectsCollected
      description: Objects collected during gc
    PythonGcObjectsUncollectable:
      properties:
        generation:
          type: string
          title: Generation
      type: object
      title: PythonGcObjectsUncollectable
      description: Uncollectable objects found during GC
    PythonGcCollections:
      properties:
        generation:
          type: string
          title: Generation
      type: object
      title: PythonGcCollections
      description: Number of times this generation was collected
    PythonInfo:
      type: object
      title: PythonInfo
      description: Python platform information
    ProcessVirtualMemoryBytes:
      properties: {}
      type: object
      title: ProcessVirtualMemoryBytes
      description: Virtual memory size in bytes.
    ProcessResidentMemoryBytes:
      properties: {}
      type: object
      title: ProcessResidentMemoryBytes
      description: Resident memory size in bytes.
    ProcessStartTimeSeconds:
      properties: {}
      type: object
      title: ProcessStartTimeSeconds
      description: Start time of the process since unix epoch in seconds.
    ProcessCpuSeconds:
      properties: {}
      type: object
      title: ProcessCpuSeconds
      description: Total user and system CPU time spent in seconds.
    ProcessOpenFds:
      properties: {}
      type: object
      title: ProcessOpenFds
      description: Number of open file descriptors.
    ProcessMaxFds:
      properties: {}
      type: object
      title: ProcessMaxFds
      description: Maximum number of open file descriptors.
```

## Real advanced FastAPI example:

```python
# For openapi_tags field, application should be instanciated normally, not using
# fastapi.openapi.utils.get_openapi() function.
app = FastAPI(
    title=__prog__,
    summary=summary,
    description=__doc__,
    version=f"{__version__} {__status__}",
    contact={"name": __author__, "email": __email__},
    openapi_tags=[
        {"name": "Internal", "description": "Internal endpoints."},
    ],
    docs_url=None,
    redoc_url=None,
)

# Genearate metrics schema and save default method with another name.
metrics_schema = prometheus_client_to_openapi(metrics=REGISTRY)
app.default_openapi = app.openapi


# This way custom schema (for metrics) is prepended to OpenAPI specification.
def custom_openapi() -> dict[str, Any]:
    """Modify default OpenAPI spec for metrics to be documented."""

    # This should be called only once, obviously.
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = app.default_openapi()
    openapi_schema["components"]["schemas"].update(metrics_schema)

    # FastAPI inserts "type" parameter here so ReDoc cannot handle custom schema
    # reference.
    del openapi_schema["paths"]["/metrics"]["get"]["responses"]["200"]["content"]["application/openmetrics-text"]["schema"]["type"]

    # Also remove default 422 Validation Error from documentation since there is
    # no actual validation of Accept header, just some kind of negotiation to
    # support "Accept: application/openmetrics-text".
    del openapi_schema["paths"]["/metrics"]["get"]["responses"]["422"]

    app.openapi_schema = openapi_schema
    return openapi_schema


# Now replace default .openapi() method with custom.
app.openapi = custom_openapi
```

And handler:

```python
class MetricsResponse(Response):
    """Prometheus-compatible metrics response."""

    media_type = "application/openmetrics-text"

    def render(self, content: Any) -> bytes:
        return generate_latest()


def serve_metrics(
    accept: Annotated[
        str | None,
        Header(
            description="Accept HTTP header for content-type negotiation with Prometheus server.",
            examples=["application/openmetrics-text", "text/plain"],
        ),
    ] = None,
) -> MetricsResponse:
    """Serve application metrics."""

    if accept is not None and "application/openmetrics-text" in accept.lower():
        return MetricsResponse(media_type="application/openmetrics-text")

    return MetricsResponse(media_type="text/plain")


router.add_api_route(
    path="/metrics",
    endpoint=serve_metrics,
    name="Metrics",
    description="Get application metrics in Prometheus-compatible format.",
    response_class=MetricsResponse,
    responses={
        status.HTTP_200_OK: {
            "content": {
                "application/openmetrics-text": {
                    "schema": {
                        "$ref": "#/components/schemas/PrometheusClientMetrics",
                    },
                },
                "text/plain": {
                    "schema": {
                        "$ref": "#/components/schemas/PrometheusClientMetrics",
                    },
                },
            },
        },
    },
)
```

## Changelog:

- `1.0.2`: (18.10.2025): redo label descriptions, commented code.
- `1.0.1`: (27.09.2025): remove `required` field completely.

## TODO

- Add [`aioprometheus`](https://pypi.org/project/aioprometheus/) support
