import logging
import os
from typing import Any

from fastapi.responses import JSONResponse, RedirectResponse
from fastapi import FastAPI, Request, Body


from python_activator.Manifest import Manifest
from python_activator.loader import set_object_directory
from python_activator.exceptions import (
    EndpointNotFoundError,
    KONotFoundError,
    InvalidInputParameterError,
)

app = FastAPI()
Knowledge_Objects = {}
Routing_Dictionary = {}
object_directory = ""

@app.exception_handler(EndpointNotFoundError)
@app.exception_handler(KONotFoundError)
@app.exception_handler(InvalidInputParameterError)
async def custom_exception_handler(request, exc):
    return JSONResponse(content={"title": exc.title,"detail": exc.detail,}, status_code=exc.status_code,)


async def custom_middleware(request: Request, call_next):
    path = request.url.path
    if path.startswith("/endpoints/") and request.method == "POST":
        logging.info(f"Request to endpoint {path}")

        response = await call_next(request)

        logging.info(f"Response to endpoint {path}: {response.status_code}")
    elif path.startswith("/kos/") and request.method == "POST":
        logging.info(f"Request to ko {path}")

        response = await call_next(request)

        logging.info(f"Response to ko {path}: {response.status_code}")    
    else:
        response = await call_next(request)

    return response


app.middleware("http")(custom_middleware)


@app.get(
    "/",
    include_in_schema=False,
)
async def root(request: Request):
    response = RedirectResponse(url="/docs")
    return response


@app.get("/endpoints")
def endpoints(request: Request):
    return [{"@id":key, **obj} for key, obj in Routing_Dictionary.items()]


@app.get("/endpoints/{endpoint_path:path}")
async def endpoint_detail(endpoint_path: str, request: Request):
    try:
        return Routing_Dictionary[endpoint_path]
    except Exception as e:
        raise EndpointNotFoundError(e)  # repr(e)


# endpoint to expose all packages
@app.post("/endpoints/{endpoint_path:path}")
async def execute_endpoint(
    endpoint_path: str,
    body: Any = Body(...),
):
    try:
        endpoint = Routing_Dictionary[endpoint_path]
    except Exception as e:
        raise EndpointNotFoundError(e)  # repr(e)

    try:
        function = endpoint["function"]
        result = function(body)
        return {
            "result": result,
            "info": {endpoint_path: endpoint, "inputs": body},
        }
    except Exception as e:
        raise InvalidInputParameterError(e)


@app.get("/kos")
def endpoints(request: Request):
    return [obj.metadata for obj in Knowledge_Objects.values()]


@app.get("/kos/{endpoint_path:path}")
async def endpoint_detail(endpoint_path: str, request: Request):
    try:
        return Knowledge_Objects[endpoint_path].metadata
    except Exception as e:
        raise KONotFoundError(e)  # repr(e)


def finalize():
    global object_directory
    object_directory = set_object_directory()
    try:
        del os.environ["COLLECTION_PATH"]
        del os.environ["MANIFEST_PATH"]
    except Exception:
        pass


# run install if the app is starated using a web server like
# "poetry run uvicorn python_activator.api:app --reload"
@app.on_event("startup")
async def startup_event():
    logging.info(">>>>>> running startup event")
    manifest = Manifest()
    manifest.load_from_manifest()
    global Knowledge_Objects, Routing_Dictionary
    Knowledge_Objects, Routing_Dictionary = manifest.install_loaded_objects()
    finalize()
