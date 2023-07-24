## Install the `python-activator`

The `python-activator` can be installed from a binary wheel (.whl)  or a source (tar.gx) available in the **Releases** section of the Github repo. It is not currently published to the Python Package Index (PyPI). Please check [Releases](https://github.com/kgrid/python-activator/releases) for the latest versions.

```bash
# install from a release
pip install https://github.com/kgrid/python-activator/releases/download/0.4-alpha/python_activator-0.1.0-py3-none-any.whl  
```

See the [development notes](#development) for [other ways to install the app](#other-ways-to-install-the-app).


## Run the app

> **Note**
> To use the command line interface (CLI) you must install the CLI as an _extra_. Add `[cli]` to the end of the `.whl` package name and quote the entire package path.

```bash 
pip install "https://github.com/kgrid/python-activator/releases/download/0.4-alpha/python_activator-0.1.0-py3-none-any.whl[cli]"
```

### Use CLI to run 

Pass --collection-path and --manifest-path as input parameters:   

```bash
python-activator run --collection-path=<path> --manifest-path=<path>`
```
 or set `COLLECTION_PATH` and/or `MANIFEST_PATH` as an environment variables. If not specified `COLLECTION_PATH` defaults to `./pyshelf`. There is no default for `MANIFEST_PATH``.

### Run the application module directly 

The `python-activator` uses [FastAPI] which needs a WSGI/ASGI server like `uvicorn` to serve it's API. If you've installed the `[cli]` extras, `uvicorn` should be available. Otherwise you can `pip install uvicorn`. See 

```bash
uvicorn --version
# Running uvicorn 0.23.1 with CPython 3.11.4 on Darwin
COLLECTION_PATH=<path> uvicorn python_activator.api:app --reload` 
```

> **Note:** 
> Don't use `--reload` outside of development workflows 

> **Note** 
> It is strongly reccommended taht you run the `python-activator` in a virtual environment to avoid placing modules loaded at runtime in your global space. Tools like `venv`, `poetry`, `pdm`, `pyenv`, etc. can make it significantly easier manage local virtual environments.

#### Test the loaded knowledge objects
Use http://127.0.0.1:8000/endpoints to get the endpoints and their status. Each endpoint is accssible via an http POST reqest (e.g.using postman) to http://127.0.0.1:8000/endpoints/{id}  with a json body.


#### python-simple-v1.0.zip:

`POST http://127.0.0.1:8000/ep/python/simple/v1.0` with body:
```json
{
    "name":"John Doe",
    "spaces":15
}
```

#### for python-multiartifact-v1-0

`POST http://127.0.0.1:8000/ep/python/multiartifact/v1.0` with body:
```json
{
    "name":"John Doe",
    "spaces":15,
    "size":25
}
```



## Development

### Setting up the project

The python-activator is a Poetry project with a `src/` layout. Poetry is use to manage dependencies, build the project, and help with teh developer workflow.

Make sure you have Python 3.10+ installed. You will use use `poetry` to create a virtual environment, install the app and it's dependencies on your machine (from source, editable, by default, includes dev dependencies)

```bash
poetry env use {python-version}
poetry install
```
Open the app in your IDE from root of the project. You may want to start a `poetry` shell.

```bash
poetry shell
code .  
# or run wrapped in a virtual environment
poetry run code .
```

You may have to point your IDE to `poetry`'s virtual environment (IDE dependant). You may also have to initialize or relaunch in-IDE terminal sessions. You can check with 

```bash
poetry env info
```
Your IDE's Python tooling and testing should work as for any Python project. Find out more about using `poetry` to manage dependencies, and build, maintainm, and publish projects here at [python-poetry.org](https://python-poetry.org/).

### Using the example collection

Check out the KO example collection from https://github.com/kgrid-objects/example-collection and start the `python-activator`. 

```bash
# for the latest versions
git clone https://github.com/kgrid-objects/example-collection.git
COLLECTION_PATH=../example-collection/collection 
uvicorn python_activator.api:app 
```

Or start the `python-activator` with a manifest and it will download objects to a local folder before installing them.

```bash
# Starting with a released collection
MANIFEST_PATH=https://github.com/kgrid-objects/example-collection/releases/download/4.2.1/manifest.json 
uvicorn python_activator.api:app 
```

### Other ways to install the app

You may want to use `--force-reinstall` when testing to replace the packeage in the current environment.

#### From local source or GitHub
```bash
pip install path/to/src/python-activator --force-reinstall
# or
pip install https://github.com/kgrid/python-activator.git  # from source --force-reinstall
```

#### from local builds (from `dist/`) during development

```bash
pip install path/to/src/python-activator/dist/python_activator-0.1.0-py3-none-any.whl
```
 


## Notes

### Known issues
Note: Multiartifact packages should not have a dot in their name as it causes issues for python domain names. Packages can have any name on their folder. If you are providing unzipped packages please rename your multiartifact packages like the following example: from  python-multiartifact-v1.0 to python-multiartifact-v1-0.
