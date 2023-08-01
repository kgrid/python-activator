import os
from typing import Any
import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request, Body
from python_activator.Manifest import Manifest

app = FastAPI()
Knowledge_Objects = {}


@app.get(
    "/",
    include_in_schema=False,
)
async def root(request: Request):
    return {
        "endpoints": request.url.__str__() + "endpoints",
        "fastapi documentation": request.url.__str__() + "docs",
        "execute": request.url.__str__() + "endpoints/{id}",
    }


@app.get("/endpoints")
def endpoints(request: Request):
    for obj_key in Knowledge_Objects:
        if Knowledge_Objects[obj_key].status == "installed":
            Knowledge_Objects[obj_key].url = (
                request.url.__str__() + "/" + Knowledge_Objects[obj_key].metadata["@id"]
            )

    return Knowledge_Objects


@app.get("/endpoints/{endpoint_key:path}")
async def endpoint_detail(endpoint_key: str):
    return Knowledge_Objects[endpoint_key]


# endpoint to expose all packages
@app.post("/endpoints/{endpoint_key:path}")
async def execute_endpoint(
    endpoint_key: str,
    body: Any = Body(...),
    content_type: str = Header(default="application/json"),
):
    try:
        result = await Knowledge_Objects[endpoint_key].execute(body)
        return result
    except KeyError as e:
        raise HTTPException(
            status_code=404, detail=({"test": e.args, "test1": e.__str__})
        )


def finalize():
    try:
        del os.environ["COLLECTION_PATH"]
        del os.environ["MANIFEST_PATH"]
    except Exception as e:
        print("error deleting env variables")

    print("-------------------\nPackages installed:")
    print("{:<4}. {:<30} {:<30} {:<30}".format("", "ID", "NAME", "STATUS"))
    for i, item in enumerate(Knowledge_Objects):
        print(
            "{:<4}. {:<30} {:<30} {:<30}".format(
                str(i),
                Knowledge_Objects[item].id,
                Knowledge_Objects[item].name[:30],
                Knowledge_Objects[item].status[:50],
            )
        )
    print("-------------------")


# run install if the app is starated using poetry run uvicorn python_activator.api:app --reload
@app.on_event("startup")
async def startup_event():
    print(">>>>>> running startup event")
    manifest = Manifest()
    manifest.load_from_manifest()
    global Knowledge_Objects
    Knowledge_Objects = manifest.install_loaded_objects()


# run virtual server when running this .py file directly for debugging. It will look for objects at {code folder}/pyshelf
if __name__ == "__main__":
    print(">>>>>running with debug<<<<<")
    os.environ["MANIFEST_PATH"] = "/home/faridsei/dev/test/manifest/manifestNew.json"
    # os.environ["MANIFEST_PATH"] = "https://github.com/kgrid-objects/example-collection/releases/download/4.2.1/manifest.json"
    os.environ["COLLECTION_PATH"] = "/home/faridsei/dev/test/pyshelf/"
    uvicorn.run(app, host="127.0.0.1", port=8001)
