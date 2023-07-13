
Note: Multiartifact packages should not have a dot in their name as it causes issues for python domain names. Packages can have any name on their folder. If you are providing unzipped packages please rename your multiartifact packages like the following example: from  python-multiartifact-v1.0 to python-multiartifact-v1-0.

## For developers to debug code:
1. set virtual env
    
    1.1 use `poetry env use {python-version}`

    1.2 use `poetry shell` to create and activate a virtual env

2. Open the app in vscode using `code .` from root of the project

3. While in the root of the project in your terminal install dependencies:
    
    `poetry install`

4. Open api.py and set breakpoints and run debugger by clicking on Run and Debug icon, selecting Run and Debug and setting the file type to python if not already done. Feel free to change the collection path which is hardcoded for debugging in api.py.

## For installing the app from .whl

1. Create build files (.whl and .tar.gz) using the following command in the root of the app

    `poetry build`

2. Install the app from .whl file using:
    `pip install {path}/python-activator/dist/python_activator-0.1.0-py3-none-any.whl --force-reinstall`

## Run the app
There are 5 different ways of running this app. The last 4 require the app to be installed either using poetry install  for development environment or installingfrom the .whl file for prod

1. Run the app using debugger (object_directory and manifest_path are hardcoded at the buttom of api.py for debugging)

2. Use CLI to run and pass --collection-path and --manifest-path as input parameters:   

`python-activator run --collection-path={your collection path} --manifest-path={your manifest path}`

3. Use CLI to run the app by setting COLLECTION_PATH and MANIFEST_PATH as an environment variables:    

`COLLECTION_PATH={your collection path} MANIFEST_PATH={your manifest path} python-activator run`

4. Use cli with no path provided. It will consider {root of app}/pyshelf as object location.

`python-activator run`

5.Run the app using uvicorn command and pass the object path using environment variables. 

`COLLECTION_PATH={your collection path} poetry run uvicorn python_activator.api:app --reload` 

If running in a virtual environment you could also use 

`COLLECTION_PATH={your collection path} MANIFEST_PATH={your manifest path} uvicorn python_activator.api:app --reload`

## Use loaded knowledge objects
Use http://127.0.0.1:8000/endpoints to get the endpoints and their status


Send an http POST reqest using postman to http://127.0.0.1:8000/ep/{package id from metadata}  to test it. Provide input using the approperiate format in the body of the request. i.e. json
    
    use http://127.0.0.1:8000/ep/python/simple/v1.0
    with 
    `{
    "name":"farid",
    "spaces":10
    }`
    for python-simple-v1.0.zip

    and http://127.0.0.1:8000/ep/python/multiartifact/v1.0 with 
    `{
    "name":"farid",
    "spaces":10,
    "size":25
    }`
    for python-multiartifact-v1-0








