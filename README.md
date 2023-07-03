## For developers to debug code:
1. set virtual env
    
    1.1 use `poetry env use {python-version}`

    1.2 use `poetry shell` to create and activate a virtual env

2. Open the app in vscode using `code .` from root of the project

3. While in to the root of the project in your terminal install dependencies:
    
    `poetry install`

4. Set breakpoints and run debugger by clicking on Run and Debug icon, selecting Run and Debug and setting the file type to python if not done already

## For developers
poetry run uvicorn python_activator.api:app --reload
or make sure running in a shell (may be close terminal in vscode and reopen. it should show left side the virtual env that is activated.) and use uvicorn python_activator.api:app --reload
## For installing and running the app

1. Create build files (.whl and .tar.gz) using the following command in the root of the app

    `poetry build`

2. Install the app from .whl file using:
    `pip install {path}/python-activator/dist/python_activator-0.1.0-py3-none-any.whl --force-reinstall`

3. Run the app using uvicorn

    `uvicorn python_activator.api:app`

4. Send an http POST reqest using postman to http://127.0.0.1:8000/{name of package}  to test it. Use the following json format for the body of the request:
    
    `{
        "name":"MyName",
        "spaces":20
    }`

    for included packages in this commit use http://127.0.0.1:8000/python-simple-v1.0
    with 
    `{
    "name":"farid",
    "spaces":10
    }`

    and http://127.0.0.1:8000/python-html-v1.0 with 
    `{
    "name":"farid",
    "spaces":10,
    "size":25
    }`

    Note: For Now you can use any endpoint name since it will use hardcoded package name for every endpoint name. The package name is located at {path}/python-activator/src/python_activator/pyshelf/






