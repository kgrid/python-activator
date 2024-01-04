# Python Activator
Python activator is a reference implementation of [Knowledge Grid Activator Specification](https://kgrid.org/specs/activationSpec.html), and it adheres meticulously to this specification. It serves as a reliable and compliant model for the activation of computable biomedical knowledge objects as per the specified guidelines. 

In the course of implementing the Python activator, certain aspects of the application required nuanced considerations due to rules that were not explicitly defined or were presented with a degree of flexibility in the specifications. To see more detail on these customizations and adaptations, please see [Customizations and Adaptations](#customizations-and-adaptations) section.

In areas where the specifications did not explicitly define rules for certain aspects of the application, the Python activator was implemented with additional features, incorporating assumptions, and following certain approaches, ensuring that they do not infringe upon or violate the specification. To see more detail about these features and assumptions, you can referto the [Extended Features and Implementation Considerations](#extended-features-and-implementation-considerations) section. 

## Install the `python-activator`

The `python-activator` can be installed from a binary wheel (.whl)  or a source (tar.gx) available in the **Releases** section of the GitHub repo. It is not currently published to the Python Package Index (PyPI). Please check [Releases](https://github.com/kgrid/python-activator/releases) for the latest versions.

```bash
# install from a release
pip install https://github.com/kgrid/python-activator/releases/download/0.7/python_activator-0.7-py3-none-any.whl  
```

See the [development notes](#development) for [other ways to install the app](#other-ways-to-install-the-app-during-development).


## Run the app
### Environment variables
When running the Python activator, a path to a manifest file could be provided as a list of knowledge objects to be activated and their locations. This path could be provided using ORG_KGRID_PYTHON_ACTIVATOR_MANIFEST_PATH as an environment variable or --manifest-path as an input parameter to the cli command. The knowledge objects that are listed on the manifest will be loaded to a cache location that would be used for activation. The location of this cache folder could be provided using ORG_KGRID_PYTHON_ACTIVATOR_COLLECTION_PATH as an environment variable or --collection-path as an unput parameter to the cli command. If no cache folder is provided the activator will use ./pyshelf by default. The activator creates a local manifest file in the cache when it loads knowledge objects before activating them. If you have a cache that already have loaded knowledge objects with a local manifest, you can run an activator and just provide the cache location as the collection path without an input manifest path to load the same knowledge objects from the cache.

### Use CLI to run 

> **Note**
> To use the command line interface (CLI) you must install the CLI as an _extra_. Add `[cli]` to the end of the `.whl` package name and quote the entire package path.

```bash 
pip install "python-activator[cli]@https://github.com/kgrid/python-activator/releases/download/0.7/python_activator-0.7-py3-none-any.whl"
```

Pass --collection-path and --manifest-path as input parameters:   

```bash
python-activator run --collection-path=<path> --manifest-path=<path>`
```
 or set `ORG_KGRID_PYTHON_ACTIVATOR_COLLECTION_PATH` and/or `ORG_KGRID_PYTHON_ACTIVATOR_MANIFEST_PATH` as an environment variables. Input parameters Override environment variables. If not specified `ORG_KGRID_PYTHON_ACTIVATOR_COLLECTION_PATH` defaults to `./pyshelf`. There is no default for `ORG_KGRID_PYTHON_ACTIVATOR_MANIFEST_PATH`.

 For examples of this command see [Using reference objects](#using-reference-objects) or [Using other legacy examples](#using-other-legacy-examples)

### Run the application module directly 

The `python-activator` uses [FastAPI] which needs a WSGI/ASGI server like `uvicorn` to serve it's API. If you've installed the `[cli]` extras, `uvicorn` should be available. Otherwise you can `pip install uvicorn`. See 

```bash
uvicorn --version
# Running uvicorn 0.23.1 with Python 3.11.4 on Darwin
ORG_KGRID_PYTHON_ACTIVATOR_COLLECTION_PATH=<path> uvicorn python_activator.api:app --reload 
```

> **Note:** 
> Don't use `--reload` outside of development workflows. 

> **Note:** 
> It is strongly recommended that you run the `python-activator` in a virtual environment to avoid placing modules loaded at runtime in your global space. Tools like `venv`, `poetry`, `pdm`, `pyenv`, etc. can make it significantly easier manage local virtual environments.

>**Note:**
>   If you are getting an error like ModuleNotFoundError: No module named 'python_activator', it is most likely that you are not running uvicorn from the same directory as where you have your python-activator installed. Use the following two commands to check if they are running from the same location:
>  ```bash
>  which python-activator
>  # /home/username/.pyenv/shims/python-activator
>  which uvicorn
>  # /home/username/.pyenv/shims/uvicorn
>  ```
>If these two commands show two different locations you need to fix your virtual environment and your uvicorn installation.

#### Test the loaded knowledge objects
Use http://127.0.0.1:8000/kos to get the list of knowledge objects and their status.

#### Test the loaded endpoints of knowledge objects
Use http://127.0.0.1:8000/endpoints to get the endpoints and their status. Each endpoint is accessible via an http POST request (e.g. using postman) to http://127.0.0.1:8000/endpoints/{ko_id}/{endpoint_id}  with a Json body.

For activated KOs that have a service specification, the python activator provides access to swagger and OpenAPI editor for each activated KO at {server address}/kos/{KO id}/doc.

As an example, once the BMI Calculator KO (in folder bmi-calc-ko with id BMICalculator) from the reference objects is activated, a post request could be sent to `POST http://127.0.0.1:8000/endpoints/BMICalculator/bmi` with the following body to use the bmi endpoint 
```json
{
    "height": 175,
    "weight": 70,
    "unit_system": "metric"
}
```
or swagger editor could be accessed at http://127.0.0.1:8000/kos/BMICalculator/doc for this KO to test  its endpoint.

## Development

### Setting up the project

The python-activator is a Poetry project with a `src/` layout. Poetry is used to manage dependencies, build the project, and help with the developer workflow.

Make sure you have Python 3.10+ installed. You will use `poetry` to create a virtual environment, install the app and its dependencies on your machine (from source, editable, by default, includes dev dependencies)

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

You may have to point your IDE to `poetry`'s virtual environment (IDE dependent). You may also have to initialize or relaunch in-IDE terminal sessions. You can check with 

```bash
poetry env info
```
Your IDE's Python tooling and testing should work as for any Python project. Find out more about using `poetry` to manage dependencies, and build, maintain, and publish projects here at [python-poetry.org](https://python-poetry.org/).

### Using reference objects
This activator supports [kgrid 2.0 Knowledge objects](https://github.com/kgrid/koio/blob/master/kgrid_knowledge_objects.md). [Reference Knowledge Objects Collection](https://github.com/kgrid/reference-objects) has knowledge objects that have API services implemented for Python activator. A [Local Manifest file](https://github.com/kgrid/reference-objects/blob/main/local_manifest.json) is provided in this repository to help loading these KOs from a cloned location. Clone this repository using

    ```
    git clone https://github.com/kgrid/reference-objects.git
    ``` 
Then run the Python activator and give the path to the cloned repository as the collection path. for example:

    ```
    ORG_KGRID_PYTHON_ACTIVATOR_COLLECTION_PATH=/home/code/reference-objects  uvicorn python_activator.api:app --port=8000
    ```
### Using other legacy examples
The new activator does not support legacy knowledge objects. But examples of kgrid 1.0 knowledge objects that are updated to be activated by this version of activator are included in ./tests/fixtures/installfiles/ in this repository. A manifest file is also located in this folder for testing.  

Use the following command, from the root of this repository to deploy these knowledge objects to the python activator:
```bash
 ORG_KGRID_PYTHON_ACTIVATOR_MANIFEST_PATH=./tests/fixtures/installfiles/manifest.json uvicorn python_activator.api:app
```

### Other ways to install the app during development

You may want to use `--force-reinstall` when trying to replace the app in the current environment.

#### From local source or GitHub
```bash
pip install path/to/src/python-activator --force-reinstall
# or
pip install https://github.com/kgrid/python-activator.git  # from source --force-reinstall
```

#### from local builds (from `dist/`) during development

```bash
pip install path/to/src/python-activator/dist/python_activator-0.7-py3-none-any.whl
```
## Knowledge Object Development
The Python activator supports [kgrdi 2.0 knowledge objects](https://github.com/kgrid/koio/blob/master/kgrid_knowledge_objects.md). kgrid 1.0 knowledge objects, however require some minor updates to work with Python activator:
1. The folder name containing those KOs should not contain any ".". So existing KO folders need to be renamed. 
2. The python code artifacts should to be restructured as an installable python package.
3. The deployment files need to be restructured using the following example:
    ```
    /{route name}:
      post:
        engine: 
          name: org.kgrid.python-activator
          package: {package name}
          module: {module name}
          function: {function name}
    ```
4. the server field of the service specification file should contain the value with the following format:
    ```
    servers:
    - url: /endpoints/{ko_id}
    ```

For kgrid 2.0 knowledge objects, the python implementation of API services should be structured as installable python packages.

## Deployment
To Deploy on Heroku the requiremens.txt file needs to be updated using
```
poetry export --without-hashes > requirements.txt 
```

A Procfile is also needed for Heroku deployment with the following content
```
web: uvicorn src.python_activator.api:app --host=0.0.0.0 --port=${PORT:-5000}
```

Environment variables needs to be setup under Config Vars on Heroku.

## Customizations and Adaptations
In the course of implementing the Python activator, certain aspects of the application required nuanced considerations due to rules that were not explicitly defined or were presented with a degree of flexibility in the specifications. This section outlines the thoughtful customizations and adaptations made during the development process to address such scenarios. By delving into the rationale behind each modification, we aim to provide transparency into how these tailored adjustments enhance the overall functionality of the activator while maintaining alignment with the overarching goals outlined in the specifications. Our commitment to adherence and optimization ensures a robust and tailored implementation that complements the specified guidelines.

Python activator uses ORG_KGRID_PYTHON_ACTIVATOR_MANIFEST_PATH as the environment variable name for the path to a manifest file. This activator supports Local and remote Paths for manifest path. Local Paths could be absolute or relative to the current working directory.

When using manifest file, this activator only accepts zipped knowledge objects. The local or remote (URL) paths to zip files should be listed on the input manifest. Relative local paths of zip files on the manifest file will be resolved towards the location of the manifest file. 

The activator creates an unzipped local copy of KOs and a local manifest file in the cache folder when it activates knowledge objects from a manifest. (See [local manifest file created for reference objects](https://github.com/kgrid/reference-objects/blob/main/local_manifest.json) as an example of local manifest). This activator us able to unzip remote zip files.

If no manifest path is provided, Python activator can activate knowledge objects from a local cache that contains unzipped knowledge objects and the local manifest. 

The activator uses ORG_KGRID_PYTHON_ACTIVATOR_COLLECTION_PATH as an environment variable for the location of the cache. If it is not provided it will use ./pyshelf as a relative path. 

Python activators reports loading status and errors for all KOs at {server address}/kos.

The Python activator supports kgrid 2.0 knowledge objects. kgrid 1.0 knowledge objects, however, require some [minor updates](#knowledge-object-development) to work with Python activator

## Extended Features and Implementation Considerations 
In areas where the specifications did not explicitly define rules for certain aspects of the application, the Python activator was implemented with additional features, incorporating assumptions and following certain approaches. It's important to note that these additions were made carefully, ensuring that they do not infringe upon or violate the specified guidelines. While the specification did not impose constraints in these particular areas, the implemented features align with the overall objectives and principles outlined in the specifications, contributing to a more comprehensive and robust implementation.

The Python activator has a cli implemented that lets user run the application. Collection path and local manifest could be provided as input parameters to the cli commands using --collection-path and --manifest-path respectively.

The python activator provides access to swagger and OpenAPI editor for each activated KO at {server address}/kos/{KO id}/doc. It uses the provided service specification file for this, to enable users to try service endpoints.

The python activator provides access to service specification file at {server address}/kos/{KO id}/service

If a KO has more than one service, this version of Python activator will only activate the last service.

If a service has more than one endpoint with the same name, the Python activator will keep and route to the last one.

### Known issues
Note: Multiartifact packages should not have a dot in their name as it causes issues for python domain names. Packages can have any name on their folder. If you are providing unzipped packages please rename your packages like the following example: from  python-multiartifact-v1.0 to python-multiartifact-v1-0.

## Related links
- [Kgrid Website](https://kgrid.org/)
- [Knowledge Grid Activator Specifications](https://kgrid.org/specs/activationSpec.html) 
- [JavaScrirpt Activator](https://github.com/kgrid/javascript-activator)
- [kgrid Reference Objects](https://github.com/kgrid/reference-objects)
- [Kgrid Knowledge Objects](https://github.com/kgrid/koio/blob/master/kgrid_knowledge_objects.md) 
- [Knowledge Object Implementation Ontology (KOIO)](https://github.com/kgrid/koio)
