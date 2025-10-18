"""Helper functions."""


def snake_to_pascal(v: str) -> str:
    """
    Convert string from snake_case to PascalCase.

    Args:
        v: snake_case string

    Returns:
        PascalCase string.
    """

    return "".join(word.title() for word in v.split("_"))


def normalize_describe_labels(
    describe_labels: dict[str, dict[str, str]] | None,
) -> dict[str, dict[str, str]]:
    """
    Convert possible None to dict so no empty dictionary as default value.

    Also insures metric and label names are lowercased.

    Args:
        describe_labels: Mapping metric names to dictionaries with label names
        and descriptions (from main function).

    Returns:
        Normalized dictionary.
    """

    # describe_labels dictionary is done this way because technically there may be
    # different set of label names in each metric. This is forbidden by
    # documentation, but technically is possible. Anyway, on the time of software
    # initialization there may be no actual samples and metric so we can not just
    # parse labels names.
    #
    # Or then user or this library passes MetricWrapperBase iterable (e.g. Gauge()
    # or Counter()), this is not actual metrics (they are just wrappers to generate
    # actual Metrics, which are standalone Collectors) and cannot be parsed either.
    #
    # See actual prometheus_client library code about Collector() and how it binds
    # with Metric() and MetricWrapperBase() instancies if this comment is unclear.

    if describe_labels is None:
        return {}

    metric_to_labels_description: dict[str, dict[str, str]] = {}
    labels_to_description: dict[str, str] = {}

    for metric_name, labels_descriptions in describe_labels.items():
        labels_to_description.clear()

        for label_name, label_description in labels_descriptions.items():
            labels_to_description[label_name.lower()] = label_description

        metric_to_labels_description[metric_name.lower()] = labels_to_description.copy()

    return metric_to_labels_description
