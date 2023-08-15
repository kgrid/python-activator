import os

import uvicorn
from python_activator.api import app

# run virtual server when running this .py file directly for debugging.
# It will look for objects at {code folder}/pyshelf
if __name__ == "__main__":
    print(">>>>>running with debug<<<<<")
    os.environ["MANIFEST_PATH"] = (
        os.getcwd() + "/tests/fixtures/installfiles/manifest.json"
    )
    os.environ["COLLECTION_PATH"] = os.getcwd() + "/pyshelf"
    uvicorn.run(app)
