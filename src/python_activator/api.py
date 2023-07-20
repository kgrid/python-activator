import os
from pathlib import Path
import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.openapi.docs import get_swagger_ui_html
from python_activator.loader import load_packages
from python_activator.installer import install_packages


app = FastAPI()
Knowledge_Objects = {}
object_directory = ""  # used for location of knowledge objects


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="API Documentation",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get("/openapi.json", include_in_schema=False)
async def get_openapi():
    return app.openapi()


@app.get(
    "/",
    include_in_schema=False,
)
async def root(request: Request):
    return {
        "endpoints": request.url.__str__() + "endpoints",
        "execute": request.url.__str__() + "endpoints/{id}",
    }


@app.get("/endpoints")
def endpoints(request: Request):
    for obj_key in Knowledge_Objects:
        Knowledge_Objects[obj_key].url = (
            request.url.__str__() + "/" + Knowledge_Objects[obj_key].id
        )
    return Knowledge_Objects


@app.get("/endpoints/{endpoint_key:path}")
async def endpoint_detail(endpoint_key: str):
    return Knowledge_Objects[endpoint_key]


# endpoint to expose all packages
@app.post("/endpoints/{endpoint_key:path}")
async def execute_endpoint(
    endpoint_key: str, request: Request, content_type: str = Header(...)
):
    try:
        result = await Knowledge_Objects[endpoint_key].execute(request)
        return result
    except KeyError as e:
        raise HTTPException(
            status_code=404, detail=({"test": e.args, "test1": e.__str__})
        )


# run install if the app is starated using poetry run uvicorn python_activator.api:app --reload
@app.on_event("startup")
async def startup_event():
    print(">>>>>> running startup event")
    global Knowledge_Objects
    Knowledge_Objects, object_directory = load_packages()
    Knowledge_Objects = install_packages(object_directory, Knowledge_Objects)
    

# run virtual server when running this .py file directly for debugging. It will look for objects at {code folder}/pyshelf
if __name__ == "__main__":
    print(">>>>>running with debug<<<<<")
    os.environ["MANIFEST_PATH"]="/home/faridsei/dev/test/manifest/manifest.json"
    # os.environ["MANIFEST_PATH"] = "https://github.com/kgrid-objects/example-collection/releases/download/4.2.1/manifest.json"
    os.environ["COLLECTION_PATH"] = "/home/faridsei/dev/test/pyshelf/"
    uvicorn.run(app, host="127.0.0.1", port=8000)
