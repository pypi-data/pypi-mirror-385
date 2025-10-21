import logging

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse

from mocktrics_exporter import configuration, dependencies, metrics, valueModels

api = FastAPI(redirect_slashes=False)


class _HealthcheckFilter(logging.Filter):

    _HEALTH_PATH_FRAGMENTS = {"/healthz"}

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        return not any(fragment in message for fragment in self._HEALTH_PATH_FRAGMENTS)


logging.getLogger("uvicorn.access").addFilter(_HealthcheckFilter())


@api.get("/healthz")
def healthcheck() -> JSONResponse:
    return JSONResponse(content={"status": "ok"})


@api.post("/metric")
def post_metric(metric: configuration.Metric) -> JSONResponse:

    try:

        values = []
        for value in metric.values:
            values.append(value)

        try:
            dependencies.metrics_collection.get_metric(metric.name)
            return JSONResponse(
                status_code=409,
                content={"success": False, "error": "Metric already exists"},
            )
        except IndexError:
            pass

        # Create metric
        name = dependencies.metrics_collection.add_metric(
            metrics.Metric(
                metric.name,
                values,
                metric.documentation,
                metric.labels,
                metric.unit,
            )
        )
        return JSONResponse(
            status_code=201,
            content={"success": True, "name": name, "action": "created"},
        )

    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@api.post("/metric/{id}/value")
def post_metric_value(id: str, value: valueModels.MetricValue) -> JSONResponse:

    try:
        dependencies.metrics_collection.add_metric_value(id, value)
    except metrics.Metric.ValueLabelsetSizeException:
        return JSONResponse(
            status_code=419,
            content={
                "success": False,
                "error": "Value label count does not match metric label count",
            },
        )
    except metrics.Metric.DuplicateValueLabelsetException:
        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "error": "Labelset already exists",
            },
        )
    except IndexError:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": "Requested metric does not exist",
            },
        )

    return JSONResponse(
        status_code=201,
        content={"success": True, "name": id, "action": "created"},
    )


@api.get("/metric/all")
def get_metric_all() -> JSONResponse:
    return JSONResponse(
        content=[metric.to_dict() for metric in dependencies.metrics_collection.get_metrics()]
    )


@api.get("/metric/{name}")
def get_metric_by_id(name: str) -> JSONResponse:
    try:
        metric = dependencies.metrics_collection.get_metric(name)
    except IndexError:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": "Requested metric does not exist",
            },
        )
    return JSONResponse(content=metric.to_dict())


@api.delete("/metric/{id}")
def delete_metric(id: str, request: Request):
    try:
        dependencies.metrics_collection.delete_metric(id)
        return JSONResponse(status_code=200, content={"success": True})
    except IndexError:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "Requested metric does not exist"},
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@api.delete("/metric/{id}/value")
def delete_metric_value(id: str, request: Request, labels: list[str] = Query(...)):
    try:
        metric = dependencies.metrics_collection.get_metric(id)
    except IndexError:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "Requested metric does not exist"},
        )
    if len(labels) != len(metric.labels):
        return JSONResponse(
            status_code=419,
            content={
                "success": False,
                "error": "Value label count does not match metric label count",
            },
        )
    for value in metric.values:
        if all([label in value.labels for label in labels]):
            metric.values.remove(value)
            break
    else:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": "Label set found not be found for metric",
            },
        )
    return JSONResponse(content={"success": True, "name": id, "action": "deleted"})
