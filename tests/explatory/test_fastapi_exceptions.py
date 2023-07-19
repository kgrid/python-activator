from fastapi import FastAPI, HTTPException,Request
from fastapi.responses import JSONResponse,RedirectResponse
from fastapi.responses import HTMLResponse

from fastapi.openapi.docs import get_swagger_ui_html
import uvicorn

class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name

app = FastAPI()

items = {"foo": "The Foo Wrestlers"}

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )

@app.get("/unicorns/{name}")
async def read_unicorn(name: str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}

@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": items[item_id]}



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

@app.get("/", response_class=HTMLResponse)
async def root():
    response = RedirectResponse(url="/docs")
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    
    