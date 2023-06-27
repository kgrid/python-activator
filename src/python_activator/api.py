from typing import Union
from fastapi import FastAPI
#import sys
import uvicorn


app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

#@app.get("/hello")
#def read_item(path: str):
#    sys.path.append(path)  
#    return {"path":str}


#only runs virtual server when running this .py file directly for debugging
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

